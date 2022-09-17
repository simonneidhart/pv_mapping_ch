from __future__ import annotations

import logging
import multiprocessing
import queue

import sys
sys.path.append("/Users/Nicolas/Documents/edh22/pv_mapping_ch")

import pandas as pd

from PvMapping.db import Database
from PvMapping.irradiance import get_ghi, get_dni_dhi
from PvMapping.output import PVSimulator
from PvMapping.source import SourceItem
from PvMapping.source.offline import OfflineSourceThread

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def ingest() -> None:
    # Start source thread.
    ingest_queue = queue.Queue()
    source_thread = OfflineSourceThread(ingest_queue)
    source_thread.start()

    db = Database()
    meter_metadata = db.get_meters()
    output_simulator = PVSimulator()

    out_df = pd.DataFrame(
        {
            "timestamp": pd.Series(dtype="datetime64[ns]"),
            "plant_id": pd.Series(dtype="int64"),
            "power_kw": pd.Series(dtype="float64"),
        }
    )

    while True:
        try:
            item: SourceItem = ingest_queue.get(block=True, timeout=0.25)

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
            plant_ids = []
            for plant in affected_plants:
                plant_ids.append(plant.id_)

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

            # Perform batched update of real-time power estimate for all affected plants.
            for plant_id, power_kw in zip(plant_ids, estimated_powers_kw):
                out_df = pd.concat(
                    (
                        out_df,
                        pd.DataFrame(
                            {
                                "timestamp": [item.timestamp],
                                "plant_id": [plant_id],
                                "power_kw": [power_kw],
                            },
                        ),
                    )
                )

            out_df.to_pickle("./pv_real_time.pkl")

        except queue.Empty:
            pass

        except KeyboardInterrupt:
            source_thread.stop()
            break

if __name__ == "__main__":
    ingest()
