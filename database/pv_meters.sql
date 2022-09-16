-- Table containing all meters for which alliunid has data.
drop table if exists pv_meters;
create table pv_meters (
	id serial4 primary key,
	time_series_idx int4 not null,
	"name" varchar not null,
	installed_capacity_kw int4 not null,
	slope_deg int4 not null,
	lat real not null,
	lon real not null
)
