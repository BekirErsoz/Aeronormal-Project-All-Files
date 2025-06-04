import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

class DroneControlWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Drone İnsan Tespiti ve Sayma')
        self.setGeometry(100, 100, 1200, 800)

        # YOLO model dosyalarının tam yolları
        weights_path = "/Users/bekirersoz/Desktop/drone_detection/yolov3.weights"
        config_path = "/Users/bekirersoz/Desktop/drone_detection/yolov3.cfg"
        names_path = "/Users/bekirersoz/Desktop/drone_detection/coco.names"

        # Load YOLO model
        self.net = cv2.dnn.readNet(weights_path, config_path)
        self.layer_names = self.net.getLayerNames()

        # Handle output layers depending on the OpenCV version and structure of the output
        try:
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        except TypeError:
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        self.classes = []
        with open(names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Create a video capture object
        self.cap = cv2.VideoCapture(0)

        # Layout setup
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        self.control_layout = QHBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.start_button = QPushButton('Başlat', self)
        self.start_button.clicked.connect(self.start_detection)
        self.control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Durdur', self)
        self.stop_button.clicked.connect(self.stop_detection)
        self.control_layout.addWidget(self.stop_button)

        self.count_label = QLabel('İnsan Sayısı: 0', self)
        self.control_layout.addWidget(self.count_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start_detection(self):
        self.timer.start(30)  # Update frame every 30 ms

    def stop_detection(self):
        self.timer.stop()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.warning(self, 'Uyarı', 'Kamera görüntüsü alınamadı.')
            return

        people_count = self.detect_people(frame)
        self.count_label.setText(f'İnsan Sayısı: {people_count}')

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=1)
        self.image_label.setPixmap(QPixmap.fromImage(p))

    def detect_people(self, frame):
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id == 0:  # Only detect people (class_id == 0)
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        people_count = 0
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                color = (0, 255, 0)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                people_count += 1

        return people_count

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = DroneControlWidget()
    widget.show()
    sys.exit(app.exec_())