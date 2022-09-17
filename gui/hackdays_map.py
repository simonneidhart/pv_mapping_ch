import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash import Dash, dcc, html

app = Dash(__name__)

def serve_layout(df_pvin):
    px.set_mapbox_access_token('pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ')

    fig = ff.create_hexbin_mapbox(
        data_frame=df_pvin,
        lat="lat",
        lon="lon",
        nx_hexagon=30,
        animation_frame='ts',
        opacity=0.5,
        color_continuous_scale="Cividis",
        labels={"color": "Power",  "frame": "Period"},
        min_count=1,
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=35, t=0, b=0),
        mapbox={'style': 'dark'},
    )
    fig.layout.sliders[0].pad.t=20
    fig.layout.updatemenus[0].pad.t=40

    return html.Div(dcc.Graph(id='map', figure=fig))

def get_real_time_data(duration_hours: int) -> pd.DataFrame:
    # local stub
    return pd.read_pickle('../data/day_09-01.pkl')

if __name__ == "__main__":
    df = get_real_time_data(9000)
    df['ts'] = df.index.astype(str)
    app.layout = serve_layout(df)
    app.run_server(debug=True)
