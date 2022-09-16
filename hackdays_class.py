import pvlib
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.modelchain import ModelChain

import pandas as pd


class PVSimulator():

    def __init__(self):
        """
        init
        """
        cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        self.inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_'] # not really needed (since DC output is used later)
        mod_lib = pvlib.pvsystem.retrieve_sam('cecmod')
        self.modules = mod_lib['Jinko_Solar__Co___Ltd_JKM385M_72L'] # average module with efficiency of 20%
        self.temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        self.PR = 0.85
        pass


    def pv_output(self,installed_capacity,weather_data, slope, orientation, lat, lon):
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
        system = PVSystem(surface_tilt=self.slope, 
                        surface_azimuth=self.orientation+180,
                        module_parameters=self.modules,
                        inverter_parameters=self.inverter,
                        temperature_model_parameters=self.temperature_model_parameters)

        mc = ModelChain(system, location, aoi_model="no_loss",spectral_model="no_loss") # high-level interface for standardized PV modeling
        mc.run_model(weather_data)

        num_modules = round(installed_capacity*1000/self.modules.STC)
        res = mc.results.dc.p_mp*self.PR*num_modules
        ac_power = pd.DataFrame(list(res),columns=['Power_kW'])
        
        return ac_power
