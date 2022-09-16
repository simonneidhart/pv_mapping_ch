"""This module is concerned with the estimation of power production based on existing irradiance data."""
from datetime import datetime
from time import time

import pandas as pd
import pvlib
from pvlib.irradiance import erbs
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

from PvMapping.db import Database
from data_cleaning.ch_plants_metadata import PlantsMetaCH


class PVSimulator:
    def __init__(self):
        cec_inverters = pvlib.pvsystem.retrieve_sam("cecinverter")
        self.inverter = cec_inverters[
            "ABB__MICRO_0_25_I_OUTD_US_208__208V_"
        ]  # not really needed (since DC output is used later)
        mod_lib = pvlib.pvsystem.retrieve_sam("cecmod")
        self.modules = mod_lib[
            "Jinko_Solar__Co___Ltd_JKM385M_72L"
        ]  # average module with efficiency of 20%
        self.temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS["sapm"][
            "open_rack_glass_glass"
        ]
        self.PR = 0.85
        pass

    def pv_output(self, installed_capacity, weather_data, slope, orientation, lat, lon):
        """
        Simulates a electricity production profile of a PV based on the data specified
        in the weather dataframe

        Parameters
        ----------
        installed_capacity : float
            installed PV capacity in kW
        weather data : pd.DataFrame
            Irradiance column names must include ``'dni'``, ``'ghi'``, and
            ``'dhi'``. If optional columns ``'temp_air'`` and ``'wind_speed'``
            are not provided, air temperature of 20 C and wind speed of 0 m/s
            are added to the DataFrame.'
        slope : int
            slope of PV panels / roof in degree
        orientation : int
            orientation of PV panels / roof
        lat/lon : float
            latitude and longitude of PV panels (required to simulate suns position etc.)

        Returns
        ----------
        simulated pv production (kW) as pd.DataFrame
        """
        self.slope = slope
        self.orientation = orientation
        self.lat = lat
        self.lon = lon

        location = pvlib.location.Location(latitude=self.lat, longitude=self.lon)
        system = PVSystem(
            surface_tilt=self.slope,
            surface_azimuth=self.orientation + 180,
            module_parameters=self.modules,
            inverter_parameters=self.inverter,
            temperature_model_parameters=self.temperature_model_parameters,
        )

        mc = ModelChain(
            system, location, aoi_model="no_loss", spectral_model="no_loss"
        )  # high-level interface for standardized PV modeling
        mc.run_model(weather_data)

        num_modules = round(installed_capacity * 1000 / self.modules.STC)
        res = mc.results.dc.p_mp * self.PR * num_modules
        ac_power = pd.DataFrame(list(res), columns=["Power_kW"])

        return ac_power


class SimulationSinglePlant:
    def __init__(
        self,
        simulator: PVSimulator,
        pgsql_con: Database,
        plants_meta: PlantsMetaCH,
        plant_index: int,
        ghi: float,
        timestamp: datetime,
    ):
        """Simulate AC power of a single PV plant, respectively part of a plant
        for plants with mutiple orientations, and for a single timestamp

        Args:
            simulator (PVSimulator): Instance of PVSimulator
            plants_meta (PlantsMetaCH): All plants metadata
            plant_index (int): Index of the plant
            ghi (float): Global Horizontal Irradiance
            timestamp (datetime): Timestamp
        """
        self.simulator = simulator
        self.pgsql_con = pgsql_con
        self.plants_meta = plants_meta
        self.plant_index = plant_index
        self.ghi = ghi
        self.timestamp = timestamp

    def run(self):
        """Main run pipeline"""
        self.get_plant_meta()
        self.calculate_dni_dhi()
        self.calculate_output_power()
        self.save_results()

    def get_plant_meta(self):
        """Get the metadata of the plants from the global plants list"""
        self.plant_meta = self.plants_meta.get_singple_plant(self.plant_index)
        self.latitude = self.plant_meta["latitude"]
        self.longitude = self.plant_meta["longitude"]
        self.installed_power_kwp = self.plant_meta["power_plantpart_kwp"]
        self.orientation = self.plant_meta["orientation_deg"]
        self.slope = self.plant_meta["slope_deg"]

    def calculate_dni_dhi(self):
        """Calculate DNI and DHI from the GHI and Timestamp using the
        Erbs model
        """
        loc = Location(self.latitude, self.longitude)
        sol_pos = loc.get_solarposition(self.timestamp)
        zenith = sol_pos["zenith"]
        irradiance = erbs(self.ghi, zenith, self.timestamp)
        dni = float(irradiance["dni"])
        dhi = float(irradiance["dhi"])
        self.weather = pd.DataFrame(
            index=[self.timestamp], data={"dni": [dni], "dhi": [dhi], "ghi": [self.ghi]}
        )

    def calculate_output_power(self):
        start_time = time()
        sim_pac = self.simulator.pv_output(
            self.installed_power_kwp,
            self.weather,
            self.slope,
            self.orientation,
            self.latitude,
            self.longitude,
        )
        print(time() - start_time)
        self.pac_kw = sim_pac["Power_kW"][0]

    def save_results(self):
        print(
            f"SIM timestamp [{self.timestamp}] - plant [{self.plant_index}] - "
            f"PAC [{self.pac_kw} kW]"
        )
        self.pgsql_con.update_realtime_power(self.plant_index, self.pac_kw)


class SimulationAllPlants:
    def __init__(self, input_data: pd.DataFrame):
        self.input_data = input_data
        self.simulator = PVSimulator()
        self.pgsql_con = Database()
        self.run()

    def run(self):
        self.plants_meta = PlantsMetaCH()
        self.plants_iterator()

    def plants_iterator(self):
        for timestamp, row in self.input_data.iterrows():
            ghi = row["ghi"]
            plant_index = row["plant_index"]
            sim = SimulationSinglePlant(
                self.simulator,
                self.pgsql_con,
                self.plants_meta,
                plant_index,
                ghi,
                timestamp,
            )
            sim.run()


if __name__ == "__main__":
    TEST_DATA = pd.DataFrame(
        index=[
            datetime(2022, 9, 16, 12),
            datetime(2022, 9, 16, 13),
            datetime(2022, 9, 16, 14),
        ],
        data={"ghi": [600, 500, 200], "plant_index": [0, 1, 2]},
    )
    sim_all = SimulationAllPlants(TEST_DATA)
