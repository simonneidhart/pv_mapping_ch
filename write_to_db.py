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
            database=database, user=username, password=password, 
            host=host, port=port)
        print(self.connection)
    
    def update_realtime_power(self, plant_id:int, pac_kw:float):
        """ Update realtime plant power

        Args:
            plant_id (int): Index of the plant
            pac_kw (float): Realtime AC power of the plant
        """
        cursor = self.connection.cursor()
        query = f"UPDATE pv_realtime SET power_kw={pac_kw} WHERE id={plant_id}"
        print(query)
        cursor.execute(query)