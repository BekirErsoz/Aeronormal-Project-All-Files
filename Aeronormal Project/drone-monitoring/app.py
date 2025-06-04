from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('command')
def handle_command(data):
    command = data.get('command')
    # Komutları drone'a gönderme işlemleri burada yapılır
    print(f'Received command: {command}')

def generate_drone_data():
    current_lat = 41.0082
    current_lon = 28.9784
    while True:
        # Drone'un rastgele bir konumda ilerlemesini sağlamak için hareket miktarını belirleyin
        delta_latitude = random.uniform(-0.0001, 0.0001)
        delta_longitude = random.uniform(-0.0001, 0.0001)
        current_lat += delta_latitude
        current_lon += delta_longitude
        
        data = {
            'position': {
                'longitude': current_lon,
                'latitude': current_lat
            },
            'status': {
                'battery': random.randint(50, 100),  # Batarya seviyesi 50 ile 100 arasında
                'altitude': random.uniform(10, 50),  # İrtifa 10 ile 50 metre arasında
                'speed': random.uniform(0, 20),  # Hız 0 ile 20 km/h arasında
                'temperature': random.uniform(-10, 40)  # Sıcaklık -10 ile 40 °C arasında
            },
            'alerts': [
                {'message': 'Low battery'} if random.random() > 0.95 else {}
            ]
        }
        socketio.emit('drone_data', data)
        time.sleep(1)  # Verileri her saniye gönder

threading.Thread(target=generate_drone_data).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)