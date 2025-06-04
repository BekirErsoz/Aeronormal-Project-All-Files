import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QGridLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
import random
import folium
from PyQt5.QtWebEngineWidgets import QWebEngineView
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DroneSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Drone Yer Kontrol İstasyonu")
        self.setGeometry(100, 100, 1400, 900)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        self.label = QLabel("Drone Durumu: Bekleniyor", self)
        self.layout.addWidget(self.label, 0, 0, 1, 2)

        self.telemetry_label = QLabel("Telemetri: Hız=0, İrtifa=0, Yön=0", self)
        self.layout.addWidget(self.telemetry_label, 0, 2, 1, 2)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Başlat", self)
        self.start_button.clicked.connect(self.start_simulation)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Durdur", self)
        self.stop_button.clicked.connect(self.stop_simulation)
        button_layout.addWidget(self.stop_button)

        self.layout.addLayout(button_layout, 1, 0, 1, 4)

        self.canvas = DroneCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas, 2, 0, 1, 4)

        self.webview = QWebEngineView()
        self.layout.addWidget(self.webview, 0, 4, 3, 5)

        self.init_map()

        self.thread = DroneThread()
        self.thread.position_signal.connect(self.update_simulation)
        self.thread.telemetry_signal.connect(self.update_telemetry)

    def init_map(self):
        start_coords = (41.015137, 28.979530)  
        self.map = folium.Map(location=start_coords, zoom_start=12)
        self.route = folium.PolyLine([start_coords], color="blue")
        self.route.add_to(self.map)
        data = io.BytesIO()
        self.map.save(data, close_file=False)

        self.webview.setHtml(data.getvalue().decode())

    def start_simulation(self):
        self.label.setText("Drone Durumu: Uçuşta")
        self.thread.running = True
        self.thread.start()

    def stop_simulation(self):
        self.label.setText("Drone Durumu: Durduruldu")
        self.thread.running = False

    def update_simulation(self, position):
        self.canvas.update_position(position)
        self.route.locations.append(position)
        self.map.location = position
        self.map.save(io.BytesIO())  
        folium.Marker(location=position).add_to(self.map)
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webview.setHtml(data.getvalue().decode())

    def update_telemetry(self, telemetry):
        self.telemetry_label.setText(f"Telemetri: Hız={telemetry['speed']:.2f}, İrtifa={telemetry['altitude']:.2f}, Yön={telemetry['heading']:.2f}")

class DroneCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        super().__init__(fig)
        self.setParent(parent)

        self.init_plot()

    def init_plot(self):
        self.axes.set_title('Drone Konumu')
        self.axes.set_xlabel('Boylam')
        self.axes.set_ylabel('Enlem')
        self.drone_position_plot, = self.axes.plot([], [], 'ro')
        self.route_plot, = self.axes.plot([], [], 'b-')

    def update_position(self, position):
        x, y = self.drone_position_plot.get_data()
        self.drone_position_plot.set_data(list(x) + [position[1]], list(y) + [position[0]])
        self.route_plot.set_data(list(x) + [position[1]], list(y) + [position[0]])
        self.axes.set_xlim(min(list(x) + [position[1]]) - 0.01, max(list(x) + [position[1]]) + 0.01)
        self.axes.set_ylim(min(list(y) + [position[0]]) - 0.01, max(list(y) + [position[0]]) + 0.01)
        self.draw()

class DroneThread(QThread):
    position_signal = pyqtSignal(tuple)
    telemetry_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = False
        self.districts = [
            (41.0430, 29.0339),  
            (40.9900, 29.0289),  
            (40.9780, 28.8720),  
            (41.0251, 29.0157),  
            (41.0605, 28.9872)  
        ]
        self.current_index = 0

    def run(self):
        while self.running:
            position = self.districts[self.current_index]
            telemetry = {
                "speed": random.uniform(10, 100),  
                "altitude": random.uniform(100, 500),  
                "heading": random.uniform(0, 360)  
            }
            self.position_signal.emit(position)
            self.telemetry_signal.emit(telemetry)
            self.current_index = (self.current_index + 1) % len(self.districts)
            self.msleep(3000)  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulation = DroneSimulation()
    simulation.show()
    sys.exit(app.exec_())