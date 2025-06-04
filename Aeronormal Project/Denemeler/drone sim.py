import sys
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore

class DroneApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Drone Control Interface')
        self.setGeometry(100, 100, 1200, 800)
        self.video_stream = None
        self.video_stream2 = None
        self.timer = None
        self.timer2 = None
        self.recording = None
        self.night_mode = False
        self.initUI()

    def initUI(self):
        
        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        
        
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_label)
        
        
        self.video_label2 = QtWidgets.QLabel(self)
        self.video_label2.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_label2)
        
        
        self.telemetry_label = QtWidgets.QLabel(self)
        self.telemetry_label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.telemetry_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.telemetry_label)
        
        
        self.control_panel = QtWidgets.QWidget(self)
        self.control_layout = QtWidgets.QHBoxLayout(self.control_panel)
        self.layout.addWidget(self.control_panel)
        
        
        self.start_button = QtWidgets.QPushButton('Start Video', self)
        self.start_button.clicked.connect(self.start_video)
        self.control_layout.addWidget(self.start_button)
        
        
        self.stop_button = QtWidgets.QPushButton('Stop Video', self)
        self.stop_button.clicked.connect(self.stop_video)
        self.control_layout.addWidget(self.stop_button)
        
        
        self.start_button2 = QtWidgets.QPushButton('Start Second Video', self)
        self.start_button2.clicked.connect(self.start_video2)
        self.control_layout.addWidget(self.start_button2)
        
        
        self.stop_button2 = QtWidgets.QPushButton('Stop Second Video', self)
        self.stop_button2.clicked.connect(self.stop_video2)
        self.control_layout.addWidget(self.stop_button2)
        
        
        self.capture_button = QtWidgets.QPushButton('Capture Image', self)
        self.capture_button.clicked.connect(self.capture_image)
        self.control_layout.addWidget(self.capture_button)
        
       
        self.start_record_button = QtWidgets.QPushButton('Start Recording', self)
        self.start_record_button.clicked.connect(self.start_recording)
        self.control_layout.addWidget(self.start_record_button)
        
        
        self.stop_record_button = QtWidgets.QPushButton('Stop Recording', self)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.control_layout.addWidget(self.stop_record_button)
        
        
        self.night_mode_button = QtWidgets.QPushButton('Toggle Night Mode', self)
        self.night_mode_button.clicked.connect(self.toggle_night_mode)
        self.control_layout.addWidget(self.night_mode_button)
        
        
        self.move_forward_button = QtWidgets.QPushButton('Move Forward', self)
        self.move_forward_button.clicked.connect(self.move_forward)
        self.control_layout.addWidget(self.move_forward_button)
        
        self.move_backward_button = QtWidgets.QPushButton('Move Backward', self)
        self.move_backward_button.clicked.connect(self.move_backward)
        self.control_layout.addWidget(self.move_backward_button)
        
        
        self.status_bar = self.statusBar()
        
        
        self.telemetry_timer = QtCore.QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(1000)  

    def start_video(self):
        if self.video_stream is None:
            self.video_stream = cv2.VideoCapture(0)  
            if not self.video_stream.isOpened():
                self.status_bar.showMessage("Unable to open video stream.", 5000)
                self.video_stream = None
                return
            
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            self.status_bar.showMessage("Video stream started.", 5000)

    def stop_video(self):
        if self.video_stream is not None:
            self.timer.stop()
            self.video_stream.release()
            self.video_stream = None
            self.video_label.clear()
            self.status_bar.showMessage("Video stream stopped.", 5000)

    def start_video2(self):
        if self.video_stream2 is None:
            self.video_stream2 = cv2.VideoCapture(1)  
            if not self.video_stream2.isOpened():
                self.status_bar.showMessage("Unable to open second video stream.", 5000)
                self.video_stream2 = None
                return
            
            self.timer2 = QtCore.QTimer(self)
            self.timer2.timeout.connect(self.update_frame2)
            self.timer2.start(30)
            self.status_bar.showMessage("Second video stream started.", 5000)

    def stop_video2(self):
        if self.video_stream2 is not None:
            self.timer2.stop()
            self.video_stream2.release()
            self.video_stream2 = None
            self.video_label2.clear()
            self.status_bar.showMessage("Second video stream stopped.", 5000)

    def update_frame(self):
        if self.video_stream is not None:
            ret, frame = self.video_stream.read()
            if ret:
                if self.night_mode:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame = cv2.applyColorMap(frame, cv2.COLORMAP_HOT)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                step = channel * width
                qImg = QtGui.QImage(image.data, width, height, step, QtGui.QImage.Format_RGB888)
                self.video_label.setPixmap(QtGui.QPixmap.fromImage(qImg))
                if self.recording is not None:
                    self.recording.write(frame)
            else:
                self.status_bar.showMessage("Failed to read frame.", 5000)
                self.stop_video()

    def update_frame2(self):
        if self.video_stream2 is not None:
            ret, frame = self.video_stream2.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                step = channel * width
                qImg = QtGui.QImage(image.data, width, height, step, QtGui.QImage.Format_RGB888)
                self.video_label2.setPixmap(QtGui.QPixmap.fromImage(qImg))
            else:
                self.status_bar.showMessage("Failed to read frame from second stream.", 5000)
                self.stop_video2()

    def capture_image(self):
        if self.video_stream is not None:
            ret, frame = self.video_stream.read()
            if ret:
                save_path = 'captured_image.png'
                cv2.imwrite(save_path, frame)
                self.status_bar.showMessage(f"Image saved to {save_path}", 5000)
            else:
                self.status_bar.showMessage("Failed to capture image.", 5000)

    def start_recording(self):
        if self.video_stream is not None and self.recording is None:
            self.recording = cv2.VideoWriter('recorded_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
            self.status_bar.showMessage("Recording started.", 5000)
        
    def stop_recording(self):
        if self.recording is not None:
            self.recording.release()
            self.recording = None
            self.status_bar.showMessage("Recording stopped.", 5000)

    def toggle_night_mode(self):
        self.night_mode = not self.night_mode
        if self.night_mode:
            self.status_bar.showMessage("Night mode enabled.", 5000)
        else:
            self.status_bar.showMessage("Night mode disabled.", 5000)

    def move_forward(self):
        
        self.status_bar.showMessage("Moving forward", 2000)
        print("Moving forward")

    def move_backward(self):
        
        self.status_bar.showMessage("Moving backward", 2000)
        print("Moving backward")

    def update_telemetry(self):
        
        import random
        altitude = random.uniform(0, 100)  
        speed = random.uniform(0, 50)  
        battery = random.uniform(20, 100)  
        
        
        telemetry_text = (
            f"Altitude: {altitude:.2f} m\n"
                        f"Altitude: {altitude:.2f} m\n"
            f"Speed: {speed:.2f} km/h\n"
            f"Battery: {battery:.2f} %"
        )
        
        
        self.telemetry_label.setText(telemetry_text)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DroneApp()
    mainWindow.show()
    sys.exit(app.exec_())