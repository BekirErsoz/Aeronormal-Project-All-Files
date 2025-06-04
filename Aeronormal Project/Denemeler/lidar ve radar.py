import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DroneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Radar ve Lidar Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.ax_radar = self.figure.add_subplot(121, polar=True)
        self.ax_lidar = self.figure.add_subplot(122, projection='3d')
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every second
        
        self.show()
    
    def update_plot(self):
        self.ax_radar.clear()
        self.ax_lidar.clear()
        
        # Radar data simulation
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.abs(np.sin(2 * theta) * np.cos(2 * theta))
        self.ax_radar.plot(theta, r, color='b')
        self.ax_radar.set_title("Radar Verisi")
        
        # Lidar data simulation
        x = np.random.random(100)
        y = np.random.random(100)
        z = np.random.random(100)
        self.ax_lidar.scatter(x, y, z, c='r', marker='o')
        self.ax_lidar.set_title("Lidar Verisi")
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DroneApp()
    sys.exit(app.exec_())