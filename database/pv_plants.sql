-- Table containing all PV plants in Switzerland.
DROP TABLE IF EXISTS pv_plants;
CREATE TABLE pv_plants (
    id serial4,
    plant_id integer not null,
    zipcode integer not null,
    lat real not null,
    long real not null,
    power_kw real null,
    nearest_meter_id integer null,
    constraint nearest_meter_id_fkey foreign key (nearest_meter_id) references pv_meters.id
);
