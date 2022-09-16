import psycopg2 as pg
import os
import dotenv

dotenv.load_dotenv()


host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("DATABASE")

print(host, port, username, password, database)

connection = pg.connect(database=database, user=username, password=password, host=host, port=port)
print(connection)
example_value = 22
example_id = 1
cursor = connection.cursor()
cursor.execute("UPDATE pv_realtime SET power_kw=%s WHERE id=%s", (example_value, example_id))



