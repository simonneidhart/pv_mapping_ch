import plotly.figure_factory as ff
import plotly.express as px
import numpy as np

px.set_mapbox_access_token("pk.eyJ1IjoiY2hyaXN0b3BoaHVuemlrZXIiLCJhIjoiY2pqc2swc253Mnd0aTN3cGJucG41dWExOSJ9.6mhBXjFCMSzNQRk8u6LTHQ")
np.random.seed(0)

N = 500
n_frames = 12
lat = np.concatenate([
    np.random.randn(N) * 0.5 + np.cos(i / n_frames * 2 * np.pi) + 10
    for i in range(n_frames)
])
lon = np.concatenate([
    np.random.randn(N) * 0.5 + np.sin(i / n_frames * 2 * np.pi)
    for i in range(n_frames)
])
frame = np.concatenate([
    np.ones(N, int) * i for i in range(n_frames)
])

fig = ff.create_hexbin_mapbox(
    lat=lat, lon=lon, nx_hexagon=15, animation_frame=frame,
    color_continuous_scale="Cividis", labels={"color": "Point Count", "frame": "Period"},
    opacity=0.5, min_count=1,
    show_original_data=True, original_data_marker=dict(opacity=0.6, size=4, color="deeppink")
)
fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
fig.layout.sliders[0].pad.t=20
fig.layout.updatemenus[0].pad.t=40
fig.show()
