from flask import Flask, jsonify
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq  # Doğru şekilde import edildi
import plotly.express as px
import pandas as pd
import threading
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paho.mqtt.client as mqtt
import json

# Flask Sunucusu
server = Flask(__name__)

# Dash Uygulaması
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Başlangıç Verisi
initial_data = {
    "time": [pd.Timestamp.now()],
    "altitude": [random.uniform(50, 200)],
    "battery": [random.uniform(20, 100)],
    "speed": [random.uniform(5, 20)],
    "temperature": [random.uniform(20, 30)]
}
df = pd.DataFrame(initial_data)

# MQTT Ayarları
MQTT_BROKER = "test.mosquitto.org"  # Genel MQTT broker adresi
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

# Veri Simülasyonu Fonksiyonu
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

# Simülasyonu Başlat
thread = threading.Thread(target=simulate_data)
thread.start()

@server.route('/data', methods=['GET'])
def get_data():
    return jsonify(df.tail(60).to_dict(orient='records'))  # Son 60 kaydı döner

# Dash Arayüz Düzeni
app.layout = dbc.Container([
    dcc.Interval(id='interval-component', interval=60000, n_intervals=0),
    dbc.Row([
        dbc.Col(html.H1("Drone Analiz ve Raporlama Uygulaması"), className="text-center my-4")
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

# Callbacks
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
    response = get_data()
    data = response.json
    df = pd.DataFrame(data)

    latest_row = df.iloc[-1]

    altitude_fig = px.line(df, x='time', y='altitude', title='İrtifa Zaman Grafiği')
    battery_fig = px.line(df, x='time', y='battery', title='Pil Seviyesi Zaman Grafiği')
    speed_fig = px.line(df, x='time', y='speed', title='Hız Zaman Grafiği')
    temperature_fig = px.line(df, x='time', y='temperature', title='Sıcaklık Zaman Grafiği')

    return (latest_row['altitude'], latest_row['battery'], latest_row['speed'], latest_row['temperature'],
            altitude_fig, battery_fig, speed_fig, temperature_fig)

# Rapor Oluşturma ve Gönderme
def send_email(subject, body, to):
    sender_email = "youremail@example.com"
    receiver_email = to
    password = "yourpassword"
    smtp_server = "smtp.example.com"  # SMTP sunucu adresi
    smtp_port = 587  # SMTP portu

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Otomatik Raporlama Fonksiyonu
def generate_report():
    while True:
        time.sleep(86400)  # Günlük raporlama
        report_body = f"""
        Drone Uçuş Raporu

        İrtifa Ortalaması: {df['altitude'].mean()}
        Pil Seviyesi Ortalaması: {df['battery'].mean()}
        Hız Ortalaması: {df['speed'].mean()}
        Sıcaklık Ortalaması: {df['temperature'].mean()}
        """
        send_email("Günlük Drone Raporu", report_body, "receiver@example.com")

# Raporlama Simülasyonunu Başlat
report_thread = threading.Thread(target=generate_report)
report_thread.start()

# Uygulamayı çalıştır
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)