import logging
import os

import dotenv
import pandas as pd
import psycopg2 as pg
import sqlalchemy.engine
from sqlalchemy import create_engine

from PvMapping.models import Meter, Plant

dotenv.load_dotenv()
log = logging.getLogger(__name__)


class Database:
    """Abstraction layer for database access."""

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        self.username = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.database = os.getenv("POSTGRES_DATABASE")

        log.info(
            f"Connecting to DB using {self.host=}, {self.port=}, {self.username=}, {self.password=}, {self.database=}"
        )

        self.connection = pg.connect(
            database=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def get_sqlalchemy_engine(self) -> sqlalchemy.engine.Engine:
        return create_engine(
            "postgresql://"
            + self.username
            + ":"
            + self.password
            + "@"
            + self.host
            + ":"
            + self.port
            + "/"
            + self.database
        )

    def update_realtime_power(self, plant_ids: list[int], powers_kw: list[float]):
        """Update the real-time power production for plants.

        Args:
            plant_ids: The primary keys of the plants to update.
            powers_kw: The estimated power production of each plant in kilowatts.
        """
        if len(plant_ids) != len(powers_kw):
            raise ValueError("Same number of plant_ids and powers_kw required")

        cursor = self.connection.cursor()
        for plant_id, power_kw in zip(plant_ids, powers_kw):
            cursor.execute(
                "UPDATE pv_plants SET power_kw=%s WHERE id=%s", (power_kw, plant_id)
            )
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

    def get_meters(self) -> dict[int, Meter]:
        """Get metadata of the existing meters.

        Returns
        -------
        dict[int, Meter]
            All meters.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, utility, lat, lon, installed_capacity_kw, slope_deg, orientation_deg, municipality, address "
            "FROM pv_meters"
        )
        rows = cursor.fetchall()
        meters = {
            row[0]: Meter(
                id_=row[0],
                utility=row[1],
                lat=row[2],
                lon=row[3],
                installed_capacity_kw=row[4],
                slope_deg=row[5],
                orientation_deg=row[6],
                municipality=row[7],
                address=row[8],
            )
            for row in rows
        }
        self.connection.commit()
        return meters

    def get_total_realtime_power(self) -> float:
        """Get the total power being produced in real time.

        Returns
        -------
        float:
            The total produced power [kW].
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT SUM(power_kw) FROM pv_plants")
        row = cursor.fetchone()
        self.connection.commit()
        return row[0]

    def get_affected_plants(self, meter_id: int) -> list[Plant]:
        """Get all plants whose power estimate is affected by the irradiance estimate of a meter.

        Parameters
        ----------
        meter_id:
            The ID of the meter

        Returns
        -------
        list[Plant]
            The plants whose nearest meter is the given meter.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, xtf_id, lat, lon, installed_capacity_kw, slope_deg, orientation_deg, municipality, address, zipcode, canton, nearest_meter_id, power_kw "
            "FROM pv_plants WHERE nearest_meter_id = %s",
            (meter_id,),
        )
        rows = cursor.fetchall()
        plants = [
            Plant(
                id_=row[0],
                xtf_id=row[1],
                lat=row[2],
                lon=row[3],
                installed_capacity_kw=row[4],
                slope_deg=row[5],
                orientation_deg=row[6],
                municipality=row[7],
                address=row[8],
                zipcode=row[9],
                canton=row[10],
                nearest_meter_id=row[11],
                power_kw=row[12],
            )
            for row in rows
        ]
        self.connection.commit()
        return plants
