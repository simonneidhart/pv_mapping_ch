CREATE TABLE pv_realtime (
  id BIGSERIAL PRIMARY KEY,
  plant_id INTEGER NOT NULL,
  zipcode INTEGER NOT NULL,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  power_kW REAL
);














