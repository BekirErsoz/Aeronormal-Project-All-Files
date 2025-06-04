import sys
import random
import cv2
import folium
import io
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QComboBox, QSlider, QFormLayout
import pyqtgraph as pg

class DroneSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aeron Drone Kontrol")
        self.setGeometry(100, 100, 1400, 900)
        
        # Öznitelikleri tanımla
        self.current_flight_mode = "Dengeli"
        self.speed_limit = 20
        self.altitude_limit = 100
        self.battery_threshold = 20
        self.gps_accuracy = 5

        self.initUI()

    def initUI(self):
        # Ana widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Ana layout
        main_layout = QVBoxLayout(central_widget)

        # Üst Panel (Durum Göstergeleri)
        status_bar = QHBoxLayout()
        self.battery_label = QLabel("🔋 Pil: %100", self)
        self.gps_label = QLabel("📡 GPS: Bağlı", self)
        self.mode_label = QLabel(f"🚁 Mod: {self.current_flight_mode}", self)

        for widget in [self.battery_label, self.gps_label, self.mode_label]:
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet("font-size: 18px; color: #ffffff;")
            status_bar.addWidget(widget)

        main_layout.addLayout(status_bar)

        # Orta Bölüm (Grafik ve Harita)
        graph_layout = QHBoxLayout()

        # Hız ve Yükseklik Grafikleri
        self.speed_graph = pg.PlotWidget()
        self.speed_graph.setTitle("Hız (m/s)", color="c")
        self.altitude_graph = pg.PlotWidget()
        self.altitude_graph.setTitle("Yükseklik (m)", color="c")

        # Estetik için grafik özellikleri
        self.speed_graph.setBackground('w')
        self.altitude_graph.setBackground('w')
        
        pen_speed = pg.mkPen(color=(255, 0, 0), width=2)
        pen_altitude = pg.mkPen(color=(0, 0, 255), width=2)

        self.speed_line = self.speed_graph.plot(pen=pen_speed)
        self.altitude_line = self.altitude_graph.plot(pen=pen_altitude)

        graph_layout.addWidget(self.speed_graph)
        graph_layout.addWidget(self.altitude_graph)

        # Harita Entegrasyonu (Istanbul Haritası)
        self.map_widget = QWebEngineView()
        self.update_map(41.015137, 28.979530)  # İstanbul'un başlangıç koordinatları
        graph_layout.addWidget(self.map_widget)

        main_layout.addLayout(graph_layout)

        # Alt Panel (Buton Bar)
        button_bar = QHBoxLayout()

        buttons = [
            ("Uçuş Verileri", self.show_flight_data),
            ("Görev Planlayıcı", self.show_mission_planner),
            ("Kamera Görünümü", self.show_camera_view),
            ("Telemetri", self.show_telemetry),
            ("Harita Görünümü", self.show_map_view),
            ("Ayarlar", self.show_settings)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet("background-color: #2ecc71; color: white; font-size: 16px; padding: 10px 20px;")
            button_bar.addWidget(btn)

        main_layout.addLayout(button_bar)

        # Alt Mesaj Barı
        self.message_label = QLabel("Sistem Mesajları ve Bildirimler")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("background-color: #34495e; color: white; font-size: 18px; padding: 10px;")
        main_layout.addWidget(self.message_label)

        # Simülasyon için Zamanlayıcı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(2000)  # Simülasyonu yavaşlatmak için 2 saniyede bir güncelle

    def update_simulation(self):
        # Simüle edilen hız, yükseklik, pil ve koordinat verilerini güncelle
        speed = random.uniform(0, self.speed_limit)
        altitude = random.uniform(0, self.altitude_limit)
        battery_level = max(0, random.randint(0, 100) - random.randint(0, 10))  # Pil yavaşça azalır
        latitude = random.uniform(40.98, 41.05)  # İstanbul için rastgele enlem
        longitude = random.uniform(28.95, 29.05)  # İstanbul için rastgele boylam

        self.battery_label.setText(f"🔋 Pil: %{battery_level}")
        self.mode_label.setText(f"🚁 Mod: {self.current_flight_mode}")
        
        self.speed_line.setData([speed])  # Yeni veriyle güncelle
        self.altitude_line.setData([altitude])  # Yeni veriyle güncelle

        self.message_label.setText(f"Simülasyon Çalışıyor: Hız: {speed:.2f} m/s, Yükseklik: {altitude:.2f} m, Pil: %{battery_level}, Enlem: {latitude:.4f}, Boylam: {longitude:.4f}")

        self.update_map(latitude, longitude)

        # Rastgele bilgileri sakla
        self.current_speed = speed
        self.current_altitude = altitude
        self.current_battery = battery_level
        self.current_latitude = latitude
        self.current_longitude = longitude

    def update_map(self, lat, lon):
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], tooltip="Drone Konumu").add_to(m)
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map_widget.setHtml(data.getvalue().decode())

    def show_flight_data(self):
        content = f"Şu anki Hız: {self.current_speed:.2f} m/s\nŞu anki Yükseklik: {self.current_altitude:.2f} m\nEnlem: {self.current_latitude:.4f}\nBoylam: {self.current_longitude:.4f}"
        self.open_new_window("Uçuş Verileri", content)

    def show_mission_planner(self):
        content = f"Planlanmış Görev Bilgisi: \nHız: {random.uniform(0, self.speed_limit):.2f} m/s\nYükseklik: {random.uniform(10, self.altitude_limit):.2f} m"
        self.open_new_window("Görev Planlayıcı", content)

    def show_camera_view(self):
        self.camera_window = QDialog(self)
        self.camera_window.setWindowTitle("Kamera Görünümü")
        self.camera_window.setGeometry(200, 200, 640, 480)
        
        layout = QVBoxLayout(self.camera_window)
        self.camera_label = QLabel(self.camera_window)
        layout.addWidget(self.camera_label)
        
        self.capture = cv2.VideoCapture(0)  # Bilgisayar kamerasını aç

        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera)
        self.camera_timer.start(30)  # 30 ms güncelleme süresi
        
        self.camera_window.exec_()
        
        self.capture.release()
        cv2.destroyAllWindows()

    def update_camera(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(image))

    def show_telemetry(self):
        content = f"Telemetri Verileri:\nHız: {self.current_speed:.2f} m/s\nYükseklik: {self.current_altitude:.2f} m\nPil Seviyesi: %{self.current_battery}\nEnlem: {self.current_latitude:.4f}\nBoylam: {self.current_longitude:.4f}"
        self.open_new_window("Telemetri", content)

    def show_map_view(self):
        content = f"Harita Üzerindeki Konum:\nEnlem: {self.current_latitude:.4f}\nBoylam: {self.current_longitude:.4f}"
        self.open_new_window("Harita Görünümü", content)

    def show_settings(self):
        self.settings_window = QDialog(self)
        self.settings_window.setWindowTitle("Ayarlar")
        self.settings_window.setGeometry(200, 200, 400, 400)

        layout = QFormLayout(self.settings_window)

        # Uçuş Modları
        self.flight_mode_combo = QComboBox(self.settings_window)
        self.flight_mode_combo.addItems(["Dengeli", "Performans", "Güç Tasarrufu"])
        self.flight_mode_combo.currentTextChanged.connect(self.update_flight_mode)
        layout.addRow("Uçuş Modu:", self.flight_mode_combo)

        # Hız Limiti
        self.speed_limit_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.speed_limit_slider.setRange(0, 50)
        self.speed_limit_slider.setValue(self.speed_limit)
        self.speed_limit_slider.valueChanged.connect(self.update_speed_limit)
        layout.addRow("Hız Limiti (m/s):", self.speed_limit_slider)

        # İrtifa Limiti
        self.altitude_limit_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.altitude_limit_slider.setRange(0, 200)
        self.altitude_limit_slider.setValue(self.altitude_limit)
        self.altitude_limit_slider.valueChanged.connect(self.update_altitude_limit)
        layout.addRow("İrtifa Limiti (m):", self.altitude_limit_slider)

        # GPS Hassasiyeti
        self.gps_accuracy_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.gps_accuracy_slider.setRange(1, 10)
        self.gps_accuracy_slider.setValue(self.gps_accuracy)
        self.gps_accuracy_slider.valueChanged.connect(self.update_gps_accuracy)
        layout.addRow("GPS Hassasiyeti:", self.gps_accuracy_slider)

        # Pil Alarm Eşiği
        self.battery_threshold_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.battery_threshold_slider.setRange(0, 100)
        self.battery_threshold_slider.setValue(self.battery_threshold)
        self.battery_threshold_slider.valueChanged.connect(self.update_battery_threshold)
        layout.addRow("Pil Alarm Eşiği (%):", self.battery_threshold_slider)

        # Ayarları Kapat Butonu
        close_button = QPushButton("Kapat", self.settings_window)
        close_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        close_button.clicked.connect(self.settings_window.accept)
        layout.addWidget(close_button)

        self.settings_window.exec_()

    def update_flight_mode(self, mode):
        self.current_flight_mode = mode
        if mode == "Dengeli":
            self.speed_limit = 20
            self.altitude_limit = 100
        elif mode == "Performans":
            self.speed_limit = 50
            self.altitude_limit = 200
        elif mode == "Güç Tasarrufu":
            self.speed_limit = 10
            self.altitude_limit = 50
        self.speed_limit_slider.setValue(self.speed_limit)
        self.altitude_limit_slider.setValue(self.altitude_limit)
        self.message_label.setText(f"Uçuş Modu '{mode}' olarak ayarlandı.")

    def update_speed_limit(self, value):
        self.speed_limit = value
        self.message_label.setText(f"Hız Limiti {value} m/s olarak ayarlandı.")

    def update_altitude_limit(self, value):
        self.altitude_limit = value
        self.message_label.setText(f"İrtifa Limiti {value} m olarak ayarlandı.")

    def update_gps_accuracy(self, value):
        self.gps_accuracy = value
        self.message_label.setText(f"GPS Hassasiyeti {value} olarak ayarlandı.")

    def update_battery_threshold(self, value):
        self.battery_threshold = value
        self.message_label.setText(f"Pil Alarm Eşiği %{value} olarak ayarlandı.")

    def open_new_window(self, title, content):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout(dialog)
        label = QLabel(content, dialog)
        label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(label)
        
        close_button = QPushButton("Kapat", dialog)
        close_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneSimulator()
    window.show()
    sys.exit(app.exec_())