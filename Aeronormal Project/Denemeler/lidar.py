import sys
import numpy as np
from scipy.ndimage import gaussian_filter
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DroneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gelişmiş Drone Radar ve Lidar Uygulaması")
        self.setGeometry(100, 100, 1000, 700)
        
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
    
    def update_noise_level(self):
        self.noise_level = self.noise_slider.value()

    def update_plot(self):
        self.ax_radar.clear()
        self.ax_lidar.clear()
        
        # Radar data simulation
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.abs(np.sin(2 * theta) * np.cos(2 * theta)) + np.random.normal(0, self.noise_level / 100.0, 100)
        self.ax_radar.plot(theta, r, color='b')
        self.ax_radar.set_title("Radar Verisi")
        
        # Lidar data simulation
        x = np.random.random(100)
        y = np.random.random(100)
        z = np.random.random(100)
        x = gaussian_filter(x, sigma=1)
        y = gaussian_filter(y, sigma=1)
        z = gaussian_filter(z, sigma=self.noise_level / 100.0)
        self.ax_lidar.scatter(x, y, z, c=z, cmap='viridis', marker='o')
        self.ax_lidar.set_title("Lidar Verisi")
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DroneApp()
    sys.exit(app.exec_())