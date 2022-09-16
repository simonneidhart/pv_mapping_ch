import logging
import os

import dotenv
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
        query = "UPDATE pv_plants SET power_kw=? WHERE id=?"
        cursor.execute(query, (pac_kw, plant_id))
