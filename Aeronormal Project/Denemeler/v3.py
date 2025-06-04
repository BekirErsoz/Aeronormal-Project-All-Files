import sys
import numpy as np
from scipy.ndimage import gaussian_filter
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json
import os

class DroneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gelişmiş Drone Radar ve Lidar Uygulaması")
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.ax_radar = self.figure.add_subplot(121, polar=True)
        self.ax_lidar = self.figure.add_subplot(122, projection='3d')
        
        self.initUIControls(layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every second
        
        self.show()
        
        self.data = []
        self.is_recording = False
        self.is_playing_back = False
        self.playback_index = 0

    def initUIControls(self, layout):
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)
        
        self.slider_label = QLabel("Noise Level: ")
        control_layout.addWidget(self.slider_label)
        
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setMinimum(1)
        self.noise_slider.setMaximum(100)
        self.noise_slider.setValue(10)
        self.noise_slider.valueChanged.connect(self.update_noise_level)
        control_layout.addWidget(self.noise_slider)
        
        self.noise_level = self.noise_slider.value()

        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_button)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        control_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_data)
        control_layout.addWidget(self.load_button)

        self.playback_button = QPushButton("Start Playback")
        self.playback_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.playback_button)
    
    def update_noise_level(self):
        self.noise_level = self.noise_slider.value()

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.setText("Start Recording")
        else:
            self.data = []
            self.is_recording = True
            self.record_button.setText("Stop Recording")

    def save_data(self):
        if not self.data:
            return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(self.data, file)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.data = json.load(file)
            self.playback_index = 0

    def toggle_playback(self):
        if self.is_playing_back:
            self.is_playing_back = False
            self.playback_button.setText("Start Playback")
        else:
            self.is_playing_back = True
            self.playback_button.setText("Stop Playback")

    def update_plot(self):
        self.ax_radar.clear()
        self.ax_lidar.clear()

        if self.is_playing_back and self.data:
            if self.playback_index < len(self.data):
                data_point = self.data[self.playback_index]
                self.playback_index += 1
            else:
                self.is_playing_back = False
                self.playback_button.setText("Start Playback")
                return
        else:
            data_point = self.generate_data()

        # Radar data visualization
        theta = data_point['theta']
        r = data_point['r']
        self.ax_radar.plot(theta, r, color='b')
        self.ax_radar.set_title("Radar Verisi")

        # Lidar data visualization
        x = data_point['x']
        y = data_point['y']
        z = data_point['z']
        self.ax_lidar.scatter(x, y, z, c=z, cmap='viridis', marker='o')
        self.ax_lidar.set_title("Lidar Verisi")

        self.canvas.draw()

        if self.is_recording:
            self.data.append(data_point)

    def generate_data(self):
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.abs(np.sin(2 * theta) * np.cos(2 * theta)) + np.random.normal(0, self.noise_level / 100.0, 100)
        x = np.random.random(100)
        y = np.random.random(100)
        z = np.random.random(100)
        x = gaussian_filter(x, sigma=1)
        y = gaussian_filter(y, sigma=1)
        z = gaussian_filter(z, sigma=self.noise_level / 100.0)

        return {'theta': theta.tolist(), 'r': r.tolist(), 'x': x.tolist(), 'y': y.tolist(), 'z': z.tolist()}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DroneApp()
    sys.exit(app.exec_())