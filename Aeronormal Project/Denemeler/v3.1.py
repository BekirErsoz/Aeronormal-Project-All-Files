from PyQt5.QtWidgets import (QMainWindow, QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QApplication, QMessageBox, QFileDialog, QComboBox, QSlider, QFormLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QImage, QPixmap
import sys
import pandas as pd
import json
import pyqtgraph as pg
import random
import cv2
import numpy as np
import matplotlib.pyplot as plt

class MapBridge(QObject):
    pointSelected = pyqtSignal(float, float)

    @pyqtSlot(float, float)
    def sendPoint(self, lat, lon):
        self.pointSelected.emit(lat, lon)

class DroneControlWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Drone Kontrol ve Rota Planlama')
        self.setGeometry(100, 100, 1600, 1000)

        # Web engine view to display the map
        self.map_view = QWebEngineView()

        # Create bridge object
        self.map_bridge = MapBridge()

        # Layout and map initialization
        self.init_map()

        # Line edits for latitude and longitude inputs
        self.start_label = QLabel('Başlangıç Noktası (enlem, boylam):', self)
        self.start_lat_edit = QLineEdit(self)
        self.start_lon_edit = QLineEdit(self)

        self.dest_label = QLabel('Hedef Noktalar:', self)
        self.dest_list = QListWidget(self)
        self.add_dest_button = QPushButton('Hedef Ekle', self)
        self.add_dest_button.clicked.connect(self.add_destination)

        self.remove_dest_button = QPushButton('Hedefi Kaldır', self)
        self.remove_dest_button.clicked.connect(self.remove_destination)

        # Button to add points from Excel file
        self.upload_button = QPushButton('Excel Dosyası Yükle', self)
        self.upload_button.clicked.connect(self.load_from_excel)

        # Button to create route
        self.create_route_button = QPushButton('Rota Oluştur', self)
        self.create_route_button.clicked.connect(self.create_route)

        # Button to start simulation
        self.start_sim_button = QPushButton('Simülasyonu Başlat', self)
        self.start_sim_button.clicked.connect(self.start_simulation)

        # Button to stop simulation
        self.stop_sim_button = QPushButton('Simülasyonu Durdur', self)
        self.stop_sim_button.clicked.connect(self.stop_simulation)

        # Hız, Yükseklik, Batarya Sıcaklık ve Radar Grafikleri
        self.speed_graph = pg.PlotWidget()
        self.speed_graph.setTitle("Hız (m/s)", color="c")
        self.altitude_graph = pg.PlotWidget()
        self.altitude_graph.setTitle("Yükseklik (m)", color="c")
        self.battery_temp_graph = pg.PlotWidget()
        self.battery_temp_graph.setTitle("Batarya Sıcaklığı (%)", color="c")

        # Estetik için grafik özellikleri
        self.speed_graph.setBackground('w')
        self.altitude_graph.setBackground('w')
        self.battery_temp_graph.setBackground('w')

        pen_speed = pg.mkPen(color=(255, 0, 0), width=2)
        pen_altitude = pg.mkPen(color=(0, 0, 255), width=2)
        pen_battery_temp = pg.mkPen(color=(0, 255, 0), width=2)

        self.speed_line = self.speed_graph.plot(pen=pen_speed)
        self.altitude_line = self.altitude_graph.plot(pen=pen_altitude)
        self.battery_temp_line = self.battery_temp_graph.plot(pen=pen_battery_temp)

        # Radar grafiği için QPixmap
        self.radar_label = QLabel(self)
        self.radar_label.setFixedSize(300, 300)

        # Durum göstergeleri
        self.battery_label = QLabel("🔋 Pil: %100", self)
        self.gps_label = QLabel("📡 GPS: Bağlı", self)
        self.mode_label = QLabel(f"🚁 Mod: Dengeli", self)

        for widget in [self.battery_label, self.gps_label, self.mode_label]:
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet("font-size: 18px; color: #ffffff;")

        # Üst Panel
        status_bar = QHBoxLayout()
        status_bar.addWidget(self.battery_label)
        status_bar.addWidget(self.gps_label)
        status_bar.addWidget(self.mode_label)

        # Alt Mesaj Barı
        self.message_label = QLabel("Sistem Mesajları ve Bildirimler")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("background-color: #34495e; color: white; font-size: 18px; padding: 10px;")

        # Simülasyon için Zamanlayıcı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

        # Buton Bar
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

        # Layout setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vbox = QVBoxLayout(central_widget)
        vbox.addLayout(status_bar)  # Üst paneli ekle
        vbox.addWidget(self.map_view)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.start_label)
        hbox1.addWidget(self.start_lat_edit)
        hbox1.addWidget(self.start_lon_edit)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.dest_label)
        hbox2.addWidget(self.dest_list)
        hbox2.addWidget(self.add_dest_button)
        hbox2.addWidget(self.remove_dest_button)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.upload_button)
        hbox3.addWidget(self.create_route_button)
        hbox3.addWidget(self.start_sim_button)
        hbox3.addWidget(self.stop_sim_button)

        # Grafikler için yan yana layout
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.speed_graph)
        graph_layout.addWidget(self.altitude_graph)
        graph_layout.addWidget(self.battery_temp_graph)
        graph_layout.addWidget(self.radar_label)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(graph_layout)
        vbox.addLayout(button_bar)
        vbox.addWidget(self.message_label)

        self.dest_points = []  # List to store destination points
        self.start_point = None  # Store the starting point
        self.simulation_running = False  # Flag to check if simulation is running

        # Video capture for camera view
        self.cap = cv2.VideoCapture(0)

        # Initialize simulation parameters
        self.flight_mode = "Dengeli"
        self.speed_limit = 20
        self.altitude_limit = 100
        self.gps_accuracy = 5
        self.battery_threshold = 20
        self.battery_temp = 30  # Varsayılan batarya sıcaklığı

        # Variables to store simulated data
        self.simulated_speeds = []
        self.simulated_altitudes = []
        self.simulated_battery_temps = []

    def init_map(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OpenStreetMap</title>
            <script src="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.js"></script
                        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.css" />
            <style>html, body { height: 100%; margin: 0; }</style>
        </head>
        <body>
            <div id="mapid" style="height: 100%;"></div>
            <script>
                var map = L.map('mapid').setView([41.0082, 28.9784], 10);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                }).addTo(map);

                var markers = [];
                var bridge = null;
                var vehicleMarker = null; // Marker for the vehicle
                var simulationInterval = null; // Interval for simulation
                var stopSimulationFlag = false; // Flag to stop simulation

                map.on('click', function(e) {
                    if (bridge !== null) {
                        bridge.sendPoint(e.latlng.lat, e.latlng.lng);
                    }
                });

                function addMarker(lat, lon, label) {
                    var marker = L.marker([lat, lon], {icon: L.icon({iconUrl: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'})}).addTo(map)
                        .bindPopup(label)
                        .openPopup();
                    markers.push(marker);
                }

                function createDirectLine(startLat, startLon, destLat, destLon) {
                    L.polyline([[startLat, startLon], [destLat, destLon]], {color: 'red'}).addTo(map);
                }

                function startSimulation(startLat, startLon, points) {
                    if (vehicleMarker) {
                        map.removeLayer(vehicleMarker);
                    }

                    var index = 0;
                    vehicleMarker = L.marker([startLat, startLon], {
                        icon: L.icon({iconUrl: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png'}) // Vehicle marker
                    }).addTo(map);

                    function moveToNextPoint() {
                        if (index >= points.length || stopSimulationFlag) {
                            clearInterval(simulationInterval);
                            return;
                        }

                        var point = points[index];
                        var destLat = point[0];
                        var destLon = point[1];

                        var latlngs = [[startLat, startLon], [destLat, destLon]];
                        L.polyline(latlngs, {color: 'blue'}).addTo(map);

                        var startTime = new Date().getTime();
                        var duration = 5000; // Duration in milliseconds (5 seconds for demo)

                        function animateVehicle() {
                            var elapsedTime = new Date().getTime() - startTime;
                            var progress = Math.min(elapsedTime / duration, 1);

                            var currentLat = startLat + progress * (destLat - startLat);
                            var currentLon = startLon + progress * (destLon - startLon);

                            vehicleMarker.setLatLng([currentLat, currentLon]);

                            if (progress < 1) {
                                requestAnimationFrame(animateVehicle);
                            } else {
                                vehicleMarker.setLatLng([destLat, destLon]);
                                startLat = destLat;
                                startLon = destLon;
                                index++;
                                setTimeout(moveToNextPoint, 1000); // Move to the next point after 1 second
                            }
                        }

                        animateVehicle();
                    }

                    moveToNextPoint();
                }

                function stopSimulation() {
                    stopSimulationFlag = true;
                }

                // Expose functions to PyQt
                window.stopSimulation = stopSimulation;
            </script>
        </body>
        </html>
        """

        # Set up the bridge
        self.setup_bridge()

        # Load HTML content into the map view
        self.map_view.setHtml(html_content)

    def setup_bridge(self):
        # Set up bridge after HTML content is loaded
        self.map_view.page().runJavaScript("""
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.bridge = channel.objects.bridge;
            });
        """)
        self.map_channel = QWebChannel()
        self.map_bridge = MapBridge()
        self.map_channel.registerObject("bridge", self.map_bridge)
        self.map_view.page().setWebChannel(self.map_channel)

    @pyqtSlot(float, float)
    def onPointSelected(self, lat, lon):
        # Slot to receive selected point coordinates
        self.start_lat_edit.setText(str(lat))
        self.start_lon_edit.setText(str(lon))

    def load_from_excel(self):
        # Open file dialog to select Excel file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Excel Dosyası Seçin", "", "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)", options=options)
        
        if not file_path:
            return
        
        try:
            df = pd.read_excel(file_path)

            if df.empty:
                QMessageBox.warning(self, 'Uyarı', 'Excel dosyasında veri bulunamadı.')
                return

            # Assume the first row contains the starting point
            start_point = df.iloc[0]
            start_lat = start_point['Enlem']
            start_lon = start_point['Boylam']

            # Set the starting point
            self.start_lat_edit.setText(str(start_lat))
            self.start_lon_edit.setText(str(start_lon))
            self.start_point = (start_lat, start_lon)

            # Clear existing markers and destination points
            self.map_view.page().runJavaScript("markers.forEach(marker => map.removeLayer(marker));")
            self.dest_points.clear()
            self.dest_list.clear()

            # Add markers for each point in the Excel file (excluding the first row)
            for index, row in df.iloc[1:].iterrows():
                lat = row['Enlem']
                lon = row['Boylam']
                label = f'({lat}, {lon})'
                js_command = f"addMarker({lat}, {lon}, '{label}');"
                self.map_view.page().runJavaScript(js_command)
                self.dest_points.append((float(lat), float(lon)))
                self.dest_list.addItem(label)

        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Bir hata oluştu: {str(e)}')

    def add_destination(self):
        lat = self.start_lat_edit.text()
        lon = self.start_lon_edit.text()
        if not lat or not lon:
            QMessageBox.warning(self, 'Uyarı', 'Enlem ve boylamı giriniz.')
            return
        
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            QMessageBox.warning(self, 'Hata', 'Geçerli bir enlem ve boylam giriniz.')
            return

        label = f'({lat}, {lon})'
        self.dest_list.addItem(label)
        self.dest_points.append((lat, lon))
        # Add marker for the new destination
        js_command = f"addMarker({lat}, {lon}, '{label}');"
        self.map_view.page().runJavaScript(js_command)

    def remove_destination(self):
        selected_items = self.dest_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Uyarı', 'Kaldırmak için bir hedef seçin.')
            return

        for item in selected_items:
            index = self.dest_list.row(item)
            self.dest_list.takeItem(index)
            self.dest_points.pop(index)
            # Rebuild the markers as the old marker list will be invalid
            self.map_view.page().runJavaScript("markers.forEach(marker => map.removeLayer(marker));")
            for lat, lon in self.dest_points:
                label = f'({lat}, {lon})'
                js_command = f"addMarker({lat}, {lon}, '{label}');"
                self.map_view.page().runJavaScript(js_command)

    def create_route(self):
        if len(self.dest_points) < 2:
            QMessageBox.warning(self, 'Uyarı', 'En az iki hedef nokta seçilmelidir.')
            return

        # Create routes between all points
        for i in range(len(self.dest_points) - 1):
            start_lat, start_lon = self.dest_points[i]
            end_lat, end_lon = self.dest_points[i + 1]
            js_command = f"createDirectLine({start_lat}, {start_lon}, {end_lat}, {end_lon});"
            self.map_view.page().runJavaScript(js_command)

    def start_simulation(self):
        if not self.start_point:
            QMessageBox.warning(self, 'Uyarı', 'Başlangıç noktası belirlenmemiş.')
            return

        if len(self.dest_points) < 1:
            QMessageBox.warning(self, 'Uyarı', 'En az bir hedef nokta seçilmelidir.')
            return

        start_lat, start_lon = self.start_point
        points = json.dumps(self.dest_points)  # Convert list to JSON string
        js_command = f"startSimulation({start_lat}, {start_lon}, {points});"
        self.map_view.page().runJavaScript(js_command)

        # Start the simulation updates
        self.simulation_running = True
        self.timer.start(2000)  # Update every 2 seconds

    def stop_simulation(self):
        self.simulation_running = False
        self.timer.stop()
        self.map_view.page().runJavaScript("stopSimulation();")

    def update_simulation(self):
        if not self.simulation_running:
            return
        
        # Simüle edilen hız, irtifa ve batarya sıcaklık verilerini güncelle
        speed = random.uniform(0, self.speed_limit)  # Use speed limit
        altitude = random.uniform(0, self.altitude_limit)  # Use altitude limit
        battery_temp = random.uniform(20, 40)  # Random battery temperature

        # Bu değerleri grafiklerde göstermek için listelere ekleyin
        self.simulated_speeds.append(speed)
        self.simulated_altitudes.append(altitude)
        self.simulated_battery_temps.append(battery_temp)

        # Grafikler için x ekseninde zaman bilgisi ekleyin
        time = range(len(self.simulated_speeds))

        # Hız, Yükseklik ve Batarya Sıcaklığı grafikleri güncelle
        self.speed_line.setData(time, self.simulated_speeds)
        self.altitude_line.setData(time, self.simulated_altitudes)
        self.battery_temp_line.setData(time, self.simulated_battery_temps)

        # Pil durumu göstergesini güncelle
        self.battery_label.setText(f"🔋 Pil: %{random.randint(20, 100)}")

        # Radar Grafiği Güncellemesi
        self.update_radar_chart(speed, altitude, battery_temp)

        # Sistem Mesajları ve Bildirimler kısmını güncelle
        self.message_label.setText(f"Son güncelleme - Hız: {speed:.2f} m/s, İrtifa: {altitude:.2f} m, Batarya Sıcaklığı: {battery_temp:.2f} °C")

    def update_radar_chart(self, speed, altitude, battery_temp):
        # Radar grafiği için veriler
        labels = ['Hız', 'İrtifa', 'Batarya Sıcaklığı']
        stats = [speed, altitude, battery_temp]

        # Radar grafiği oluşturma
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        stats += stats[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
        ax.fill(angles, stats, color='red', alpha=0.25)
        ax.plot(angles, stats, color='red', linewidth=2)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        # Radar grafiğini QLabel'e çizdirme
        canvas = fig.canvas
        canvas.draw()
        width, height = canvas.get_width_height()
        image = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        self.radar_label.setPixmap(QPixmap.fromImage(image))

        plt.close(fig)  # Grafik alanını serbest bırak

    def show_flight_data(self):
        content = f"Şu anki Hız: {random.uniform(0, self.speed_limit):.2f} m/s\nŞu anki Yükseklik: {random.uniform(0, self.altitude_limit):.2f} m\nBatarya Sıcaklığı: {random.uniform(20, 40):.2f} °C"
        self.open_new_window("Uçuş Verileri", content)

    def show_mission_planner(self):
        if not self.dest_points:
            content = "Henüz bir rota oluşturulmadı."
        else:
            content = "Oluşturulan Rota:\n"
            for i, (lat, lon) in enumerate(self.dest_points):
                content += f"{i+1}. Nokta - Enlem: {lat}, Boylam: {lon}\n"
        self.open_new_window("Görev Planlayıcı", content)

    def show_camera_view(self):
        self.camera_window = QDialog(self)
        self.camera_window.setWindowTitle("Kamera Görünümü")
        self.camera_window.setGeometry(200, 200, 640, 480)

        layout = QVBoxLayout(self.camera_window)

        self.video_label = QLabel(self.camera_window)
        layout.addWidget(self.video_label)

        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_view)
        self.camera_timer.start(30)  # 30ms per frame (~33 FPS)

        self.camera_window.exec_()

        self.cap.release()

    def update_camera_view(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(image))
        else:
            self.camera_timer.stop()

    def show_telemetry(self):
        content = f"Telemetri Verileri:\nHız: {random.uniform(0, self.speed_limit):.2f} m/s\nYükseklik: {random.uniform(0, self.altitude_limit):.2f} m\nBatarya Sıcaklığı: {random.uniform(20, 40):.2f} °C\nPil Seviyesi: %{random.randint(self.battery_threshold, 100)}"
        self.open_new_window("Telemetri", content)

    def show_map_view(self):
        if not self.dest_points:
            content = "<p>Henüz bir rota oluşturulmadı.</p>"
        else:
            content = """
            <html>
            <head>
                <title>Drone Rota Haritası</title>
                <script src="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.js"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.css" />
                <style>html, body { height: 100%; margin: 0; }</style>
            </head>
            <body>
                <div id="mapid" style="height: 400px; width: 600px;"></div>
                <script>
                    var map = L.map('mapid').setView([41.0082, 28.9784], 10);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                    }).addTo(map);
                    
                    var points = """ + json.dumps(self.dest_points) + """;
                    
                    var latlngs = [];
                    for (var i = 0; i < points.length; i++) {
                        var point = points[i];
                        L.marker([point[0], point[1]]).addTo(map);
                        latlngs.push([point[0], point[1]]);
                    }
                    
                    if (latlngs.length > 1) {
                        L.polyline(latlngs, {color: 'red'}).addTo(map);
                    }
                </script>
            </body>
            </html>
            """
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
        self.speed_limit_slider.setValue(self.speed_limit)  # Varsayılan hız limiti
        self.speed_limit_slider.valueChanged.connect(self.update_speed_limit)
        layout.addRow("Hız Limiti (m/s):", self.speed_limit_slider)

        # İrtifa Limiti
        self.altitude_limit_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.altitude_limit_slider.setRange(0, 200)
        self.altitude_limit_slider.setValue(self.altitude_limit)  # Varsayılan irtifa limiti
        self.altitude_limit_slider.valueChanged.connect(self.update_altitude_limit)
        layout.addRow("İrtifa Limiti (m):", self.altitude_limit_slider)

        # GPS Hassasiyeti
        self.gps_accuracy_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.gps_accuracy_slider.setRange(1, 10)
        self.gps_accuracy_slider.setValue(self.gps_accuracy)  # Varsayılan GPS hassasiyeti
        self.gps_accuracy_slider.valueChanged.connect(self.update_gps_accuracy)
        layout.addRow("GPS Hassasiyeti:", self.gps_accuracy_slider)

        # Pil Alarm Eşiği
        self.battery_threshold_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.battery_threshold_slider.setRange(0, 100)
        self.battery_threshold_slider.setValue(self.battery_threshold)  # Varsayılan pil alarm eşiği
        self.battery_threshold_slider.valueChanged.connect(self.update_battery_threshold)
        layout.addRow("Pil Alarm Eşiği (%):", self.battery_threshold_slider)

        # Ayarları Kapat Butonu
        close_button = QPushButton("Kapat", self.settings_window)
        close_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        close_button.clicked.connect(self.settings_window.accept)
        layout.addWidget(close_button)

        self.settings_window.exec_()

    def update_flight_mode(self, mode):
        self.mode_label.setText(f"🚁 Mod: {mode}")
        self.flight_mode = mode
        # Uçuş modu ayarlarını burada değiştirebilirsiniz

    def update_speed_limit(self, value):
        self.speed_limit = value
        print(f"Hız Limiti: {value} m/s")

    def update_altitude_limit(self, value):
        self.altitude_limit = value
        print(f"İrtifa Limiti: {value} m")

    def update_gps_accuracy(self, value):
        self.gps_accuracy = value
        print(f"GPS Hassasiyeti: {value}")

    def update_battery_threshold(self, value):
        self.battery_threshold = value
        print(f"Pil Alarm Eşiği: %{value}")

    def open_new_window(self, title, content):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(dialog)
        
        if "<html>" in content:
            # Eğer içerik HTML ise, bunu QWebEngineView'de göster
            web_view = QWebEngineView(dialog)
            web_view.setHtml(content)
            layout.addWidget(web_view)
        else:
            # Eğer normal metin ise QLabel ile göster
            label = QLabel(content, dialog)
            label.setWordWrap(True)
            label.setStyleSheet("font-size: 14px; padding: 20px;")
            layout.addWidget(label)

        close_button = QPushButton("Kapat", dialog)
        close_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DroneControlWidget()
    window.show()
    sys.exit(app.exec_())