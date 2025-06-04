import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                depth = self.simulate_depth_map(gray)
                self.change_pixmap_signal.emit(frame, depth)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

    def simulate_depth_map(self, gray_image):
        # Kenar tespiti yaparak basit bir derinlik haritası simülasyonu
        depth = cv2.Laplacian(gray_image, cv2.CV_64F)
        depth = cv2.convertScaleAbs(depth)
        return depth

class DroneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Görüntü ve Derinlik Ölçümü Uygulaması")
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.ax_depth = self.figure.add_subplot(111)
        
        self.initUIControls(layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Her saniye güncelle
        
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_images)
        self.thread.start()

        self.image_label = QLabel()
        layout.addWidget(self.image_label)
        
        self.depth_data = None
        self.is_recording = False
        self.is_playing_back = False
        self.playback_index = 0
        self.recorded_data = []
        
        self.show()

    def initUIControls(self, layout):
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

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

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def update_images(self, color_image, depth_image):
        qt_img = self.convert_cv_qt(color_image)
        self.image_label.setPixmap(qt_img)

        depth_colormap = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)
        self.depth_data = depth_colormap

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.setText("Start Recording")
        else:
            self.recorded_data = []
            self.is_recording = True
            self.record_button.setText("Stop Recording")

    def save_data(self):
        if not self.recorded_data:
            return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(self.recorded_data, file)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.recorded_data = json.load(file)
            self.playback_index = 0

    def toggle_playback(self):
        if self.is_playing_back:
            self.is_playing_back = False
            self.playback_button.setText("Start Playback")
        else:
            self.is_playing_back = True
            self.playback_button.setText("Stop Playback")

    def update_plot(self):
        self.ax_depth.clear()

        if self.is_playing_back and self.recorded_data:
            if self.playback_index < len(self.recorded_data):
                depth_data = np.array(self.recorded_data[self.playback_index])
                self.playback_index += 1
            else:
                self.is_playing_back = False
                self.playback_button.setText("Start Playback")
                return
        else:
            depth_data = self.depth_data

        if depth_data is not None:
            self.ax_depth.imshow(depth_data, cmap='jet')
            self.ax_depth.set_title("Derinlik Verisi")

            self.canvas.draw()

            if self.is_recording:
                self.recorded_data.append(depth_data.tolist())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = DroneApp()
    sys.exit(app.exec_())