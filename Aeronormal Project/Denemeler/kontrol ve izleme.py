from flask import Flask
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
import pandas as pd
import numpy as np
import random
import threading
import time


server = Flask(__name__)


app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])


initial_data = {
    "time": [pd.Timestamp.now()],
    "altitude": [random.uniform(50, 200)],
    "battery": [random.uniform(20, 100)],
    "speed": [random.uniform(5, 20)]
}
df = pd.DataFrame(initial_data)


def update_data():
    global df
    while True:
        time.sleep(1)
        new_data = pd.DataFrame({
            "time": [pd.Timestamp.now()],
            "altitude": [random.uniform(50, 200)],
            "battery": [max(0, df.iloc[-1]['battery'] - random.uniform(0, 0.5))],
            "speed": [random.uniform(5, 20)]
        })
        df = pd.concat([df, new_data], ignore_index=True)


thread = threading.Thread(target=update_data)
thread.start()


app.layout = dbc.Container([
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    dbc.Row([
        dbc.Col(html.H1("Drone Kontrol ve İzleme Sistemi Simülasyonu"), className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            daq.Gauge(
                id="altitude-gauge",
                label="İrtifa",
                min=0,
                max=500,
                value=100,
                units="m"
            ),
        ], width=4),
        dbc.Col([
            daq.Gauge(
                id="battery-gauge",
                label="Pil Seviyesi",
                min=0,
                max=100,
                value=50,
                units="%"
            ),
        ], width=4),
        dbc.Col([
            daq.Gauge(
                id="speed-gauge",
                label="Hız",
                min=0,
                max=50,
                value=10,
                units="m/s"
            ),
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="altitude-graph"),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="battery-graph"),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="speed-graph"),
        ], width=12),
    ]),
], fluid=True)


@app.callback(
    [Output('altitude-gauge', 'value'),
     Output('battery-gauge', 'value'),
     Output('speed-gauge', 'value'),
     Output('altitude-graph', 'figure'),
     Output('battery-graph', 'figure'),
     Output('speed-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    global df
    
    latest_row = df.iloc[-1]
    
    altitude_fig = px.line(df, x='time', y='altitude', title='İrtifa Zaman Grafiği')
    battery_fig = px.line(df, x='time', y='battery', title='Pil Seviyesi Zaman Grafiği')
    speed_fig = px.line(df, x='time', y='speed', title='Hız Zaman Grafiği')

    return latest_row['altitude'], latest_row['battery'], latest_row['speed'], altitude_fig, battery_fig, speed_fig


if __name__ == '__main__':
    app.run_server(debug=True)