from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QGridLayout, QHBoxLayout, QSlider, QFileDialog, QProgressBar
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QImage, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import folium
import io
import sys
import random
import numpy as np
import cv2

class DroneSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Drone Yer Kontrol İstasyonu")
        self.setGeometry(100, 100, 1600, 900)  # Genişliği artırdım

        # Başlangıç hızı, irtifası, batarya seviyesi, batarya sıcaklığı ve motor güçleri
        self.initial_speed = 80
        self.initial_altitude = 400
        self.initial_battery = 100
        self.initial_battery_temperature = 25
        self.initial_motor_power = [80, 80, 80, 80]

        # Başlangıç konumu
        self.initial_latitude = 40.748817  # Örnek koordinat: New York
        self.initial_longitude = -73.985428  # Örnek koordinat: New York

        # Haritayı oluşturma
        self.create_map()

        # Diğer UI öğeleri ve özellikleri burada tanımlanabilir

    def create_map(self):
        self.map = folium.Map(location=[self.initial_latitude, self.initial_longitude], zoom_start=15)

        # Haritaya eklemeler yapılabilir
        folium.Marker([self.initial_latitude, self.initial_longitude], tooltip='Başlangıç Konumu').add_to(self.map)

        # Haritayı widget'a yerleştirme
        data = io.BytesIO()
        self.map.save(data, close_file=False)

        self.web_view = QWebEngineView()
        self.web_view.setHtml(data.getvalue().decode())

        self.setCentralWidget(self.web_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = DroneSimulation()
    main_window.show()
    sys.exit(app.exec_())