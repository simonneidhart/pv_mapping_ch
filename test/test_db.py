import pprint
from datetime import datetime

import dotenv

from PvMapping.db import Database

dotenv.load_dotenv()


def test_get_lat_lon() -> None:
    db = Database()
    df_plants, df_meters = db.get_lat_lon()
    print(df_plants)
    print(df_meters)


def test_set_nearest_meters() -> None:
    db = Database()
    db.set_nearest_meters([0, 1, 2], [1, 2, 3])


def test_get_meter_metadata() -> None:
    db = Database()
    db.get_meters()


def test_get_real_time_data() -> None:
    db = Database()
    df = db.get_real_time_data(
        datetime.fromisoformat("2022-08-01"), datetime.fromisoformat("2022-08-02")
    )
    pprint.pp(df)


if __name__ == "__main__":
    # test_get_lat_lon()
    # test_set_nearest_meters()
    # test_get_meter_metadata()
    test_get_real_time_data()
