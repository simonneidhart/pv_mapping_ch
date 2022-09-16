import psycopg2 as pg
import os
import dotenv

dotenv.load_dotenv()

class PGSQL():
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
    
    def update_realtime_power(self, plant_id, pac_kw):
        cursor = self.connection.cursor()
        query = f"UPDATE pv_realtime SET power_kw={pac_kw} WHERE id={plant_id}"
        print(query)
        cursor.execute(query)