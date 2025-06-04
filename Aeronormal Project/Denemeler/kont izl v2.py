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
import paho.mqtt.client as mqtt
import json

server = Flask(__name__)

app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

initial_data = {
    "time": [pd.Timestamp.now()],
    "altitude": [random.uniform(50, 200)],
    "battery": [random.uniform(20, 100)],
    "speed": [random.uniform(5, 20)],
    "temperature": [random.uniform(20, 30)]
}
df = pd.DataFrame(initial_data)

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "drone/telemetry"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global df
    new_data = json.loads(msg.payload.decode())
    new_data["time"] = pd.to_datetime(new_data["time"])
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def simulate_data():
    global df
    while True:
        time.sleep(1)
        new_data = {
            "time": pd.Timestamp.now().isoformat(),
            "altitude": random.uniform(50, 200),
            "battery": max(0, df.iloc[-1]['battery'] - random.uniform(0, 0.5)),
            "speed": random.uniform(5, 20),
            "temperature": random.uniform(20, 30)
        }
        client.publish(MQTT_TOPIC, json.dumps(new_data))

thread = threading.Thread(target=simulate_data)
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
        ], width=3),
        dbc.Col([
            daq.Gauge(
                id="battery-gauge",
                label="Pil Seviyesi",
                min=0,
                max=100,
                value=50,
                units="%"
            ),
        ], width=3),
        dbc.Col([
            daq.Gauge(
                id="speed-gauge",
                label="Hız",
                min=0,
                max=50,
                value=10,
                units="m/s"
            ),
        ], width=3),
        dbc.Col([
            daq.Gauge(
                id="temperature-gauge",
                label="Sıcaklık",
                min=0,
                max=50,
                value=25,
                units="°C"
            ),
        ], width=3),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="altitude-graph"),
        ], width=6),
        dbc.Col([
            dcc.Graph(id="battery-graph"),
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="speed-graph"),
        ], width=6),
        dbc.Col([
            dcc.Graph(id="temperature-graph"),
        ], width=6),
    ]),
], fluid=True)

@app.callback(
    [Output('altitude-gauge', 'value'),
     Output('battery-gauge', 'value'),
     Output('speed-gauge', 'value'),
     Output('temperature-gauge', 'value'),
     Output('altitude-graph', 'figure'),
     Output('battery-graph', 'figure'),
     Output('speed-graph', 'figure'),
     Output('temperature-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    global df
    
    latest_row = df.iloc[-1]
    
    altitude_fig = px.line(df, x='time', y='altitude', title='İrtifa Zaman Grafiği')
    battery_fig = px.line(df, x='time', y='battery', title='Pil Seviyesi Zaman Grafiği')
    speed_fig = px.line(df, x='time', y='speed', title='Hız Zaman Grafiği')
    temperature_fig = px.line(df, x='time', y='temperature', title='Sıcaklık Zaman Grafiği')

    return (latest_row['altitude'], latest_row['battery'], latest_row['speed'], latest_row['temperature'], 
            altitude_fig, battery_fig, speed_fig, temperature_fig)

if __name__ == '__main__':
    app.run_server(debug=True)