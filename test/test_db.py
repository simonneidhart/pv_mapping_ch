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


if __name__ == "__main__":
    # test_get_lat_lon()
    test_set_nearest_meters()
