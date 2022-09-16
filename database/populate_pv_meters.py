import sqlalchemy
import os
import dotenv
import pandas as pd

"""
This file is meant to be run when the PostgreSQL instance for the API is instantiated.

.csv files which are to be loaded into the database are downloaded from URLs and
PostgreSQL tables are generated from them.
"""

dotenv.load_dotenv()

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("DATABASE")

DATABASE_URL_SQLALCHEMY = (
    "postgresql://"
    + username
    + ":"
    + password
    + "@"
    + host
    + ":"
    + port
    + "/"
    + database
)

# engine = sqlalchemy.create_engine(DATABASE_URL_SQLALCHEMY, execution_options=dict(stream_results=True))
engine = sqlalchemy.create_engine(DATABASE_URL_SQLALCHEMY)

xlsx_file_path = os.getenv("PV_METERS_PATH")

df = pd.read_excel(xlsx_file_path)
print("head of data: ", df.head())
print("Saving to table 'pv_meters'")
df.to_sql("pv_meters", engine, if_exists="replace", chunksize=5000, index=False)
