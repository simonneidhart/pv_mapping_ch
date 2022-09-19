from __future__ import annotations

import numpy as np
import pyproj

from PvMapping.db import Database


def update_nearest_neighbor() -> None:
    g = pyproj.Geod(ellps="WGS84")
    db = Database()
    plants, meters = db.get_lat_lon()
    distance_matrix = np.zeros((len(plants), len(meters)))
    for i, plant in plants.iterrows():
        for j, meter in meters.iterrows():
            distance_matrix[i, j] = g.line_length(
                [plant.lon, meter.lon], [plant.lat, meter.lat]
            )
    nearest_neighbor_indices = distance_matrix.argmin(axis=1)
    nearest_neighbor_ids = meters.iloc[nearest_neighbor_indices].id.values
    db.set_nearest_meters(
        plant_ids=[int(i) for i in plants.id.values],
        meter_ids=[int(i) for i in nearest_neighbor_ids],
    )


if __name__ == "__main__":
    update_nearest_neighbor()
