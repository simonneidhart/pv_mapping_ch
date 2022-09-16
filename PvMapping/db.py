import logging
import os

import dotenv
import pandas as pd
import psycopg2 as pg

dotenv.load_dotenv()
log = logging.getLogger(__name__)


class Database:
    """Abstraction layer for database access."""

    def __init__(self):
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        username = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DATABASE")

        log.info(
            f"Connecting to DB using {host=}, {port=}, {username=}, {password=}, {database=}"
        )

        self.connection = pg.connect(
            database=database, user=username, password=password, host=host, port=port
        )

    def update_realtime_power(self, plant_id, pac_kw):
        """Update the real-time power production for a plant.

        Args:
            plant_id: The primary key of the plant to update.
            pac_kw: The estimated power production in kilowatts.
        """
        cursor = self.connection.cursor()
        query = "UPDATE pv_plants SET power_kw=%s WHERE id=%s"
        cursor.execute(query, (pac_kw, plant_id))
        self.connection.commit()

    def get_lat_lon(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Get the latitude and longitude data of PV plants & meters.

        Returns
        -------
        tuple
            The latitude and longitude data of PV plants and the meters.
            Both dataframes contain the columns "id", "lat" and "lon".
        """
        cursor = self.connection.cursor()
        query = "SELECT id, lat, lon FROM {}"
        columns = ["id", "lat", "lon"]

        cursor.execute(query.format("pv_plants"))
        rows = cursor.fetchall()
        df_plants = pd.DataFrame(rows, columns=columns)

        cursor.execute(query.format("pv_meters"))
        rows = cursor.fetchall()
        df_meters = pd.DataFrame(rows, columns=columns)

        self.connection.commit()

        return df_plants, df_meters

    def set_nearest_meters(self, plant_ids: list[int], meter_ids: list[int]) -> None:
        """Set the nearest meters for the given PV plants.
        This meter will be used as the reference for obtaining irradiance data.

        Parameters
        ----------
        plant_ids
            The IDs of the PV plants.
        meter_ids
            The IDs of the meters.
        """
        if len(plant_ids) != len(meter_ids):
            raise ValueError("Same number of plate_ids and meter_ids required")

        cursor = self.connection.cursor()
        for plant_id, meter_id in zip(plant_ids, meter_ids):
            cursor.execute(
                "UPDATE pv_plants SET nearest_meter_id=%s WHERE id=%s",
                (meter_id, plant_id),
            )
        self.connection.commit()
