from PyQt5.QtWidgets import (QMainWindow, QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QApplication, QMessageBox, QFileDialog, QComboBox, QSlider, QFormLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWebChannel import QWebChannel
import sys
import pandas as pd
import json
import pyqtgraph as pg
import random

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

        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.speed_graph)
        graph_layout.addWidget(self.altitude_graph)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(graph_layout)
        vbox.addLayout(button_bar)
        vbox.addWidget(self.message_label)

        self.dest_points = []  # List to store destination points
        self.start_point = None  # Store the starting point
        self.simulation_running = False  # Flag to check if simulation is running

    def init_map(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OpenStreetMap</title>
            <script src="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.js"></script>
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
        self.timer.start(1000)  # Update every second

    def stop_simulation(self):
        self.simulation_running = False
        self.timer.stop()
        self.map_view.page().runJavaScript("stopSimulation();")

    def update_simulation(self):
        if not self.simulation_running:
            return
        
        # Simüle edilen hız ve yükseklik verilerini güncelle
        speed = random.uniform(0, 20)
        altitude = random.uniform(0, 100)

        self.battery_label.setText(f"🔋 Pil: %{random.randint(20, 100)}")
        self.speed_line.setData([speed])  # Yeni veriyle güncelle
        self.altitude_line.setData([altitude])  # Yeni veriyle güncelle

    def show_flight_data(self):
        content = f"Şu anki Hız: {random.uniform(0, 20):.2f} m/s\nŞu anki Yükseklik: {random.uniform(0, 100):.2f} m"
        self.open_new_window("Uçuş Verileri", content)

    def show_mission_planner(self):
        content = "Görev planlama verileri burada gösterilecek."
        self.open_new_window("Görev Planlayıcı", content)

    def show_camera_view(self):
        content = "Kamera görünümü burada gösterilecek."
        self.open_new_window("Kamera Görünümü", content)

    def show_telemetry(self):
        content = f"Telemetri Verileri:\nHız: {random.uniform(0, 20):.2f} m/s\nYükseklik: {random.uniform(0, 100):.2f} m\nPil Seviyesi: %{random.randint(20, 100)}"
        self.open_new_window("Telemetri", content)

    def show_map_view(self):
        content = "Harita görünümü burada gösterilecek."
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
        self.speed_limit_slider.setValue(20)  # Varsayılan hız limiti
        self.speed_limit_slider.valueChanged.connect(self.update_speed_limit)
        layout.addRow("Hız Limiti (m/s):", self.speed_limit_slider)

        # İrtifa Limiti
        self.altitude_limit_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.altitude_limit_slider.setRange(0, 200)
        self.altitude_limit_slider.setValue(100)  # Varsayılan irtifa limiti
        self.altitude_limit_slider.valueChanged.connect(self.update_altitude_limit)
        layout.addRow("İrtifa Limiti (m):", self.altitude_limit_slider)

        # GPS Hassasiyeti
        self.gps_accuracy_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.gps_accuracy_slider.setRange(1, 10)
        self.gps_accuracy_slider.setValue(5)  # Varsayılan GPS hassasiyeti
        self.gps_accuracy_slider.valueChanged.connect(self.update_gps_accuracy)
        layout.addRow("GPS Hassasiyeti:", self.gps_accuracy_slider)

        # Pil Alarm Eşiği
        self.battery_threshold_slider = QSlider(Qt.Horizontal, self.settings_window)
        self.battery_threshold_slider.setRange(0, 100)
        self.battery_threshold_slider.setValue(20)  # Varsayılan pil alarm eşiği
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
        # Diğer ayarlar da buradan değiştirilebilir
        print(f"Uçuş Modu: {mode}")

    def update_speed_limit(self, value):
        print(f"Hız Limiti: {value} m/s")

    def update_altitude_limit(self, value):
        print(f"İrtifa Limiti: {value} m")

    def update_gps_accuracy(self, value):
        print(f"GPS Hassasiyeti: {value}")

    def update_battery_threshold(self, value):
        print(f"Pil Alarm Eşiği: %{value}")

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DroneControlWidget()
    window.show()
    sys.exit(app.exec_())