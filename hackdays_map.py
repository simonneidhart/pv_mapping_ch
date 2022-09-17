from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

app = Dash(__name__)

n_frames = 1440


def serve_layout(ev,ev_sum):
    sMBT = 'pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ'
    px.set_mapbox_access_token(sMBT)
    #fig = px.scatter_mapbox(df_pvin, lat="lat", lon="lon", zoom=6, size=len(df_pvin) * [10])


    fig = ff.create_hexbin_mapbox(data_frame = ev,
        lat='lat', lon='lon', nx_hexagon=100, animation_frame='ts', color='kW', agg_func=np.sum,
        color_continuous_scale="Cividis", labels={"color": "PV Power [kW]", "frame": "Period"},
        opacity=0.5, min_count=1,
        show_original_data=True, original_data_marker=dict(opacity=0.6, size=4, color="deeppink")
    )


    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    fig.layout.sliders[0].pad.t=20
    fig.layout.updatemenus[0].pad.t=40

    fig.update_layout(
        autosize=False,
        width=2000,
        height=1000,
        margin=dict(l=0, r=35, t=0, b=0),
        mapbox={
            'style': 'dark',
        },
    )

    figheight=700
    line_figure = go.Figure(layout={"height":figheight})
    line_figure.add_trace(go.Scatter(x=ev_sum.index, y=ev_sum['kW'], fill='tozeroy', name='Total Power [kW]'))

    line_figure.update_layout(
        xaxis_title="Timestamp (UTC)",
        yaxis_title="kW",
    )

    return html.Div(
        children=[
            html.Div(dcc.Graph(
                id='map',
                figure=fig)),
            html.Div(dcc.Graph(
                id='sum',
                figure=line_figure))
            ]
        )



if __name__ == "__main__":
    #df_pv_measured = pd.read_excel("data/Liste_PV_available.xlsx", header=0)

    ev = pd.read_pickle('day_09-01.pkl')
    print(ev.head())

    ev['ts'] = ev.index.astype(str)

    ev_sum = ev.drop(columns=['ts','lat','lon'])
    ev_sum = ev_sum.groupby(ev_sum.index).sum()

    ev_sum.head()

    ### TO-DO :
    # 1. Read PV power [kW] of all PV systems from database
    # 2. Write callback that continiously updates the dashboard (and reads new values from database)

    app.layout = serve_layout(ev,ev_sum)
    app.run_server(debug=True)
