from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

app = Dash(__name__)


def serve_layout(df_pvin):
    sMBT = 'pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ'
    px.set_mapbox_access_token(sMBT)
    fig = px.scatter_mapbox(df_pvin, lat="lat", lon="lon", zoom=6, size=len(df_pvin) * [10])


    fig = ff.create_hexbin_mapbox(
        data_frame=df_pvin,
        lat="lat",
        lon="lon",
        nx_hexagon=10,
        opacity=0.5,
        labels={"color": "Point Count"},
        min_count=1,
        show_original_data=True,
        original_data_marker=dict(size=4, opacity=0.6, color="deeppink")
    )

    fig.update_layout(
        autosize=False,
        width=2000,
        height=1000,
        margin=dict(l=0, r=35, t=0, b=0),
        mapbox={
            'style': 'dark',
        },
    )

    return html.Div(
        dcc.Graph(
            id='map',
            figure=fig))


if __name__ == "__main__":
    df_pv_measured = pd.read_excel("data/Liste_PV_available.xlsx", header=0)
    
    ### TO-DO : 
    # 1. Read PV power [kW] of all PV systems from database
    # 2. Write callback that continiously updates the dashboard (and reads new values from database)
    
    app.layout = serve_layout(df_pv_measured)
    app.run_server(debug=True)
