-- Table containing all PV plants in Switzerland.
DROP TABLE IF EXISTS pv_plants;
CREATE TABLE pv_plants (
    id serial4,
    plant_id integer not null,
    zipcode integer not null,
    lat real not null,
    long real not null,
    power_kw real null
);
