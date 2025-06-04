import sys
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore

class DroneApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simulated Drone Control Interface')
        self.setGeometry(100, 100, 1200, 800)
        self.video_stream = None
        self.timer = None
        self.initUI()

    def initUI(self):
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(20, 20, 960, 540)
        self.video_label.setStyleSheet("background-color: black;")

        self.start_button = QtWidgets.QPushButton('Start Video', self)
        self.start_button.setGeometry(1000, 50, 150, 50)
        self.start_button.clicked.connect(self.start_video)

        self.stop_button = QtWidgets.QPushButton('Stop Video', self)
        self.stop_button.setGeometry(1000, 120, 150, 50)
        self.stop_button.clicked.connect(self.stop_video)

        self.capture_button = QtWidgets.QPushButton('Capture Image', self)
        self.capture_button.setGeometry(1000, 190, 150, 50)
        self.capture_button.clicked.connect(self.capture_image)

    def start_video(self):
        if self.video_stream is None:
            self.video_stream = cv2.VideoCapture(0)  # 0 bilgisayar kamerasını temsil eder
            if not self.video_stream.isOpened():
                QtWidgets.QMessageBox.critical(self, "Error", "Unable to open video stream.")
                self.video_stream = None
                return
            
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            QtWidgets.QMessageBox.information(self, "Info", "Video stream started.")

    def stop_video(self):
        if self.video_stream is not None:
            self.timer.stop()
            self.video_stream.release()
            self.video_stream = None
            self.video_label.clear()
            QtWidgets.QMessageBox.information(self, "Info", "Video stream stopped.")

    def update_frame(self):
        if self.video_stream is not None:
            ret, frame = self.video_stream.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                step = channel * width
                qImg = QtGui.QImage(image.data, width, height, step, QtGui.QImage.Format_RGB888)
                self.video_label.setPixmap(QtGui.QPixmap.fromImage(qImg))
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to read frame.")
                self.stop_video()

    def capture_image(self):
        if self.video_stream is not None:
            ret, frame = self.video_stream.read()
            if ret:
                save_path = 'captured_image.png'
                cv2.imwrite(save_path, frame)
                QtWidgets.QMessageBox.information(self, "Image Captured", f"Image saved to {save_path}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to capture image.")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DroneApp()
    mainWindow.show()
    sys.exit(app.exec_())