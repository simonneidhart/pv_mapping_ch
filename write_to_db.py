import psycopg2 as pg
import os
import dotenv

dotenv.load_dotenv()

class PGSQL():
    """ Instanciate PostgreSQL database connection
    """
    def __init__(self):
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        username = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("DATABASE")

        print(host, port, username, password, database)

        self.connection = pg.connect(
            database=database,
            user=username,
            password=password,
            host=host,
            port=port)
        print(self.connection)

        do_host = os.getenv("DO_POSTGRES_HOST")
        do_port = os.getenv("DO_POSTGRES_PORT")
        do_username = os.getenv("DO_POSTGRES_USER")
        do_password = os.getenv("DO_POSTGRES_PASSWORD")
        do_database = os.getenv("DO_DATABASE")

        self.do_connection = pg.connect(
            database=do_database,
            user=do_username,
            password=do_password,
            host=do_host,
            port=do_port,
            sslmode='require'
        )

    def update_realtime_power(self, plant_id: int, pac_kw: float):
        """ Update realtime plant power

        Args:
            plant_id (int): Index of the plant
            pac_kw (float): Realtime AC power of the plant
        """
        cursor = self.connection.cursor()
        query = f"UPDATE pv_realtime SET power_kw={pac_kw} WHERE id={plant_id}"
        print(query)
        cursor.execute(query)

if __name__ == '__main__':
    """ For testing purpose only
    """
    pgsql_con = PGSQL()
