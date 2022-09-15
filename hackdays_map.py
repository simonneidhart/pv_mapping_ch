
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)


def serve_layout(df_pvin):
    sMBT='pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ'
    px.set_mapbox_access_token(sMBT)
    fig = px.scatter_mapbox(df_pvin, lat="lat", lon="lon", zoom=6, size =len(df_pvin)*[10])
    fig.update_layout(autosize=False,
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
            
if __name__=="__main__":

    df_pvin = pd.read_excel("data/Liste_PV_available.xlsx",header=0) 
    app.layout = serve_layout(df_pvin)
    app.run_server(debug=True)
