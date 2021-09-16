import pandas as pd
import pydeck as pdk

import plotly.graph_objects as go
import dash
import dash_deck
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

df = pd.read_csv('sim_data.csv').sort_values(['frame', 'time'])
Y_RGB = [234, 206, 9, 200]
RED_RGB = [240, 100, 0, 200]

line_layer = pdk.Layer(
    "LineLayer",
    data=df,
    get_width=5,
    get_source_position=["Y_org", "X_org"],
    get_target_position=["Y_dest", "X_dest"],
    get_color=Y_RGB,
    picking_radius=15,
    auto_highlight=True,
    pickable=True,
)

sc_df = pd.DataFrame({'coordinates': [list(tup) for tup in zip(df.Y_dest.values, df.X_dest.values)]})

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    sc_df,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=40,
    radius_min_pixels=4,
    #     radius_max_pixels=100,
    #     line_width_min_pixels=1,
    get_position="coordinates",
    #     get_radius="exits_radius",
    get_fill_color=RED_RGB,
    get_line_color=[0, 0, 0],
)

view_state = pdk.ViewState(
    latitude=25.12, longitude=55.37
    #     , bearing=-45
    #     , pitch=60
    , zoom=9.7,
)

r = pdk.Deck(layers=[line_layer, scatter_layer], initial_view_state=view_state)

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(

    [html.Div([
        html.Div([
            dcc.Graph(id='ind', figure={}, style={"height": "100px", "width": "100px", "color": 'black'})])
    ], id="layer1"),

        html.Div([html.Div(id='graph-container')], ),
        dcc.Interval(id='interval',
                     interval=1000,
                     n_intervals=1
                     )

    ])


@app.callback([Output('graph-container', 'children'), Output('ind', 'figure')], [Input('interval', 'n_intervals')])
def update_map(n):
    if n <= max(df.frame.unique()):
        tmp_df = df[df.frame == n]
        line_layer.data = tmp_df
        r.update()
        deck_component = dash_deck.DeckGL(r.to_json(), id="deck-gl",
                                          mapboxKey="pk.eyJ1IjoiY2hvdWFpYmgiLCJhIjoiY2tsdHllZXZ5MXd3NjJvbGJocjVpcXBheSJ9.QkbyoLkqeQ9nqfje7QlJAQ.mapbox_token",
                                          style={"height": "690px", "width": "100%", "position": "relative"},
                                          tooltip=True)
        mapu = dcc.Loading(children=deck_component,
                           style={
                               'width': '55vw',
                               'height': '75vh',
                               'display': 'default'
                           })
        ind_fig = go.Figure(go.Indicator(
            mode="number+delta",
            title={'text': "Needed time", "font": {"size": 25, "color": "rgba(240, 100, 0, 200)"}},
            value=n,
            number={"font": {"size": 50, "color": "rgba(234, 206, 9,200)"}},
            delta={'reference': n - 1, "font": {"size": 15}},
        ))
        ind_fig.update_layout(paper_bgcolor="rgba(0, 0, 0, 0)", height=250, width=250)
        return mapu, ind_fig
    else:
        raise PreventUpdate


app.run_server()
