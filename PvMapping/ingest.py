from __future__ import annotations

import logging
import multiprocessing

import pandas as pd

from PvMapping.db import Database
from PvMapping.irradiance import get_ghi, get_dni_dhi
from PvMapping.output import PVSimulator

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import os
import time

import dotenv
import pandas as pd

from PvMapping.source import SourceThread, SourceItem

dotenv.load_dotenv()


def ingest() -> None:
    # Start source thread.
    db = Database()
    meter_metadata = db.get_meters()
    output_simulator = PVSimulator()

    plant_ids = db.get_all_plant_ids()
    latest_power_kw = dict(zip(plant_ids, [0.0] * len(plant_ids)))


    df = pd.read_pickle(os.environ.get("TIME_SERIES_FILE_PATH"))
    for timestamp in df.index:

        row = df.loc[timestamp].dropna()
        sample = row.sample()
        meter_id, power_kw = sample.index[0], sample.values[0]
        item = SourceItem(
            timestamp=timestamp, power_kw=power_kw, meter_id=int(meter_id)
        )

        meter = meter_metadata[item.meter_id]

        # Calculate global horizontal irradiance [W/m^2] at meter location.
        ghi = get_ghi(
            power=item.power_kw * 1e3,
            installed_capacity=meter.installed_capacity_kw * 1e3,
            slope=meter.slope_deg,
        )

        # Extrapolate DNI / DHI from GHI
        dni, dhi = get_dni_dhi(
            lat=meter.lat,
            lon=meter.lon,
            timestamp=item.timestamp,
            ghi=ghi,
        )

        # Find all plants whose power output estimate is affected by the updated measurement data,
        # then update the estimates accordingly.
        affected_plants = db.get_affected_plants(item.meter_id)
        affected_plant_ids = []
        for plant in affected_plants:
            affected_plant_ids.append(plant.id_)

        global power_estimate

        def power_estimate(plant):
            estimated_power = output_simulator.pv_output(
                installed_capacity=plant.installed_capacity_kw,
                weather_data=pd.DataFrame.from_dict(
                    {item.timestamp: [ghi, dni, dhi]},
                    orient="index",
                    columns=["ghi", "dni", "dhi"],
                ),
                slope=int(plant.slope_deg),
                orientation=int(plant.orientation_deg),
                lat=plant.lat,
                lon=plant.lon,
            )
            return estimated_power
        
        with multiprocessing.Pool() as pool:
            estimated_powers_kw = pool.map(power_estimate, affected_plants)
        
        for plant_id, estimated_power_kw in zip(affected_plant_ids, estimated_powers_kw):
            latest_power_kw[plant_id] = estimated_power_kw
        
        # Perform batched update of real-time power estimate for all affected plants.
        db.update_realtime_power(
            timestamp=item.timestamp,
            plant_ids=plant_ids,
            powers_kw=latest_power_kw.values(),
        )


if __name__ == "__main__":
    ingest()
