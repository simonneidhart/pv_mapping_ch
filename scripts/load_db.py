from __future__ import annotations

import argparse

import pandas as pd

from PvMapping.db import Database


def load_db(table: str, data_file: str) -> None:
    db = Database()
    engine = db.get_sqlalchemy_engine()

    df = pd.read_pickle(data_file)
    df.to_sql(table, engine, if_exists="replace", chunksize=5000, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A utility for initializing the database from pickle data files"
    )
    parser.add_argument("table")
    parser.add_argument("data_file")
    args = parser.parse_args()
    load_db(**vars(args))
