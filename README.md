# pv_mapping_ch
Map the total pv power produced in Switzerland in real-time

# File Overview
```
.
├── data_cleaning
│   ├── clean_pv_meters_data.ipynb
│   ├── clean_pv_plants_data.ipynb
│   ├── combine-ch-pv-systems-meta.py
│   └── timeseries_crunching.ipynb
├── PvMapping
│   ├── db.py                               # Database access layer
│   ├── frontend.py                         # Entrypoint for launching dashboard using plotly
│   ├── ingest.py                           # Entrypoint for ingest pipeline
│   ├── irradiance.py                       # Estimation of irradiance from power, as well as irradiance conversions
│   ├── models.py                           # Data model definitions
│   ├── output.py                           # Prediction of output power from irradiance data.
│   └── source                              
│       ├── __init__.py                     # Abstract base class of SourceThread
│       ├── offline.py                      # OfflineSourceThread, dummy data source for demo purposes
│       └── online.py                       # OnlineSourceThread, not implemented yet.
├── README.md
├── requirements.txt
├── scripts                                       # Utility scripts
│   ├── load_db.py                          # Create database tables from pickle files
│   └── update_nearest_neighbor.py          # Recompute distance matrix and store nearest neighbors in database.
├── test
│   ├── __init__.py
│   └── test_db.py

```

# Architecture

```mermaid
flowchart LR
  Y -->|kW, lat/lon| Z[Dashboard]

  W[PV Measurements<br>] --> V[Global Irradiation]

  V --> U[dni/dhi]
  U --> Q[kW simulated]

  X[(<b>Memory</b><br>PV Metadata<br>of all PV plants<br>of Switzerland)] --> Q
  Y[(<b>PostgreSQL</b><br>kw for each<br>PV plant of<br>Switzerland)]

  Q --> Y

```
