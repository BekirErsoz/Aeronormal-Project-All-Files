from flask import Flask
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
import pandas as pd
import random

# Flask Sunucusu
server = Flask(__name__)

# Dash Uygulaması
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Drone'dan gelen veriler için örnek veri seti
df = pd.DataFrame({
    "time": pd.date_range(start="2023-01-01", periods=100, freq='T'),
    "altitude": [random.uniform(50, 200) for _ in range(100)],
    "battery": [random.uniform(20, 100) for _ in range(100)],
    "speed": [random.uniform(5, 20) for _ in range(100)]
})

# Arayüz Düzeni
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Drone Kontrol ve İzleme Sistemi"), className="text-center my-4")
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

# Callbacks
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
    # Örnek veri setinden rastgele bir satır seçin
    row = df.sample().iloc[0]
    
    altitude_fig = px.line(df, x='time', y='altitude', title='İrtifa Zaman Grafiği')
    battery_fig = px.line(df, x='time', y='battery', title='Pil Seviyesi Zaman Grafiği')
    speed_fig = px.line(df, x='time', y='speed', title='Hız Zaman Grafiği')

    return row['altitude'], row['battery'], row['speed'], altitude_fig, battery_fig, speed_fig

# Uygulamayı çalıştır
if __name__ == '__main__':
    app.run_server(debug=True)