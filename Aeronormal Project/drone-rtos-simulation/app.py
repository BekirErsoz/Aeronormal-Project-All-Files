from flask import Flask, render_template, jsonify
from threading import Thread
import time
from rtos_simulation import RTOSSimulator

app = Flask(__name__)

# RTOS simülasyonunu başlat
simulator = RTOSSimulator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/led/<action>')
def control_led(action):
    if action == 'on':
        simulator.led_on()
    elif action == 'off':
        simulator.led_off()
    elif action == 'toggle':
        simulator.toggle_led()
    return jsonify({'status': 'success', 'action': action, 'led_state': simulator.led_state})

@app.route('/telemetry')
def telemetry():
    return jsonify({
        'counter': simulator.counter,
        'cpu_usage': simulator.cpu_usage,
        'memory_usage': simulator.memory_usage,
        'temperature': simulator.temperature,
        'humidity': simulator.humidity,
        'battery_level': simulator.battery_level,
        'network_traffic': simulator.network_traffic
    })

def run_simulation():
    simulator.run()

if __name__ == '__main__':
    # RTOS simülasyonunu ayrı bir thread'de çalıştır
    simulation_thread = Thread(target=run_simulation)
    simulation_thread.daemon = True
    simulation_thread.start()

    app.run(debug=True)