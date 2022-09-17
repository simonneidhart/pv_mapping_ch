import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash import Dash, dcc, html

from write_to_db import PGSQL

app = Dash(__name__)


def serve_layout(df_pvin):
    sMBT = 'pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ'
    px.set_mapbox_access_token(sMBT)

    fig = ff.create_hexbin_mapbox(
        data_frame=df_pvin,
        lat="lat",
        lon="lon",
        nx_hexagon=100,
        animation_frame=df_pvin['frame'],
        opacity=0.5,
        color_continuous_scale="Cividis",
        labels={"color": "Point Count",  "frame": "Period"},
        min_count=1,
        # show_original_data=True,
        # original_data_marker=dict(size=4, opacity=0.6, color="deeppink")
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=35, t=0, b=0),
        mapbox={'style': 'dark'},
    )
    fig.layout.sliders[0].pad.t=20
    fig.layout.updatemenus[0].pad.t=40

    return html.Div(dcc.Graph(id='map', figure=fig))


if __name__ == "__main__":
    do_curs = PGSQL().do_connection.cursor()
    do_curs.execute("SELECT ID, LAT, LON FROM PV_PLANTS")
    pv_plants = do_curs.fetchall()
    df_pv_plants = pd.DataFrame(pv_plants, columns=['id', 'lat', 'lon'])
    df_pv_plants['frame']=1

    df_pv_plants_2 = pd.DataFrame(pv_plants, columns=['id', 'lat', 'lon'])
    df_pv_plants_2['frame']=2

    df_pv_plants = pd.concat([df_pv_plants, df_pv_plants_2], axis=0)

    ### TO-DO : 
    # 1. Read PV power [kW] of all PV systems from database
    # 2. Write callback that continiously updates the dashboard (and reads new values from database)

    app.layout = serve_layout(df_pv_plants)
    app.run_server(debug=True)
