# pv_mapping_ch
Map the total pv power produced in Switzerland in real-time

# File Overview
```
.
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


  aliunidGW[aliunid Gateways] -->|real-time<br>mesaurements| PsqlMeasurements[(<b>pv_meters</b><br>PostgreSQL<br>database)]

  PsqlMeasurements --> ghi[Global Irradiance]

  ghi --> dni[dni/dhi]

  dni --> Simulation[Simulation]

  Simulation -->|update simulated values| PsqlPlants

  PsqlMeasurements -->|precompute nearest<br>measurement point<br>for every plant| PsqlPlants[(<b>pv_plants</b><br>PostgreSQL<br>database)]

  Pronovo[Pronovo Data] -->|Metadata for each<br>plant in Switzerland| PsqlPlants

  PsqlPlants -->|kW, lat/lon| Dashboard[Dashboard]


```

