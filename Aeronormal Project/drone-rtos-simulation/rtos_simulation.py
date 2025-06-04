import time
from threading import Thread, Lock, Event

class RTOSSimulator:
    def __init__(self):
        self.led_state = False
        self.lock = Lock()
        self.stop_event = Event()
        self.tasks = []
        self.counter = 0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.temperature = 25.0
        self.humidity = 50.0
        self.battery_level = 100.0
        self.network_traffic = 0

    def led_on(self):
        with self.lock:
            self.led_state = True
            print("LED ON")

    def led_off(self):
        with self.lock:
            self.led_state = False
            print("LED OFF")

    def toggle_led(self):
        with self.lock:
            self.led_state = not self.led_state
            print("LED TOGGLED")

    def led_task(self):
        while not self.stop_event.is_set():
            with self.lock:
                print(f"LED State: {'ON' if self.led_state else 'OFF'}")
            time.sleep(1)

    def telemetry_task(self):
        while not self.stop_event.is_set():
            with self.lock:
                self.counter += 1
                self.cpu_usage = (self.counter % 100) / 100.0  # Simüle edilmiş CPU kullanımı
                self.memory_usage = (self.counter % 50) / 50.0  # Simüle edilmiş bellek kullanımı
                self.temperature += 0.1 * (-1) ** self.counter  # Simüle edilmiş sıcaklık değişimi
                self.humidity += 0.1 * (-1) ** self.counter  # Simüle edilmiş nem değişimi
                self.battery_level -= 0.5  # Simüle edilmiş batarya kullanımı
                self.network_traffic += 10  # Simüle edilmiş ağ trafiği
                print(f"Telemetry Data: Counter={self.counter}, CPU={self.cpu_usage*100}%, Memory={self.memory_usage*100}%, Temperature={self.temperature}, Humidity={self.humidity}, Battery={self.battery_level}%, Network={self.network_traffic} bytes")
            time.sleep(2)

    def run(self):
        led_thread = Thread(target=self.led_task)
        telemetry_thread = Thread(target=self.telemetry_task)

        self.tasks.append(led_thread)
        self.tasks.append(telemetry_thread)

        for task in self.tasks:
            task.start()

        for task in self.tasks:
            task.join()

    def stop(self):
        self.stop_event.set()
        for task in self.tasks:
            task.join()