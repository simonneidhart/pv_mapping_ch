import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash import Dash, dcc, html

from datetime import datetime
import dotenv
import numpy as np
import pandas as pd
import psycopg2 as pg
import sqlalchemy.engine
from psycopg2.extras import execute_values, execute_batch
from sqlalchemy import create_engine
import os

dotenv.load_dotenv()

app = Dash(__name__)

def serve_layout(df_pvin):
    px.set_mapbox_access_token('pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ')

    fig = ff.create_hexbin_mapbox(
        data_frame=df_pvin,
        lat="lat",
        lon="lon",
        nx_hexagon=150,
        animation_frame='ts',
        color='power_kw',
        agg_func=np.sum,
        opacity=0.5,
        color_continuous_scale="Cividis",
        labels={"color": "PV Power [kW]",  "frame": "Period"},
        min_count=1,
    )

    fig.update_layout(
        autosize=True,
        width=2000,
        height=1000,
        margin=dict(l=0, r=35, t=0, b=0),
        mapbox={'style': 'dark'},

    )
    fig.layout.sliders[0].pad.t=20
    fig.layout.updatemenus[0].pad.t=40
    
    return html.Div(
        children=[
        # Header and Logo
        html.Pre(
            children=[
                html.Img(src=app.get_asset_url('aliunid.png'),
                    id = 'aliunid_logo',
                    style={'height': '60px',
                        'width': 'auto',
                        'margin-bottom': '50px',
                        'margin-left': '-35px',
                        'margin-top': '-70px',}
                ),
                html.Img(src=app.get_asset_url('hackdays.png'),
                                        id = 'hackdays',
                                        style={'height': '60px',
                                            'width': 'auto',
                                            'margin-bottom': '50px',
                                            'margin-left': '100px',
                                            'margin-top': '-70px',}
                                    ),
            ]
        ),
        # Page title
        html.H1("Real Time PV Map"),
        html.Div(dcc.Graph(id='map', figure=fig))
        ]
    )

    #return html.Div(dcc.Graph(id='map', figure=fig))

def get_real_time_data():
        """Get the real-time data for the preceding hours.
        Parameters
        ----------
        time_start
            The earliest time of the data to include
        time_end
            The latest time of the data to include
        Returns
        -------
        pd.DataFrame
            Dataframe with timestamp index and columns "power_kw", "lat", "lon".
        """
        time_start = "2022-08-01 01:00:00+00:00"
        time_end = "2022-08-01 23:00:00+00:00"
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        username = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DATABASE")
        print(password)
        connection = pg.connect(
            database=database,
            user=username,
            password=password,
            host=host,
            port=port,
        )
        cursor = connection.cursor()
        cursor.execute(
            "SELECT timestamp, power_kw, lat, lon FROM pv_real_time "
            "JOIN pv_plants ON pv_plants.id = pv_real_time.plant_id "
            "WHERE timestamp BETWEEN %s AND %s "
            "ORDER BY timestamp DESC",
            (time_start, time_end),
        )
        data = cursor.fetchall()
        connection.commit()
        df = pd.DataFrame(data=data, columns=["timestamp", "power_kw", "lat", "lon"])
        df = df.set_index("timestamp")
        df.to_csv('export_csv.csv')
        return df

if __name__ == "__main__":
    df = get_real_time_data()
    df['ts'] = df.index.astype(str)
    app.layout = serve_layout(df)
    app.run_server(host="0.0.0.0", port=4200)
