import os

import dotenv
import pandas as pd
import sqlalchemy

dotenv.load_dotenv()

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DATABASE")

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

df = pd.read_pickle("/home/mathis/Downloads/pv_meters.pkl")
df.to_sql("pv_meters", engine, if_exists="replace", chunksize=5000, index=False)
