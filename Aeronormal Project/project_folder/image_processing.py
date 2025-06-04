import cv2
import tensorflow as tf
import numpy as np
import os

# TensorFlow model yükleme
model_path = "ssd_mobilenet_v2_fpnlite_320x320/saved_model"
if not os.path.exists(os.path.join(model_path, "saved_model.pb")):
    raise IOError(f"Model dosyası bulunamadı: {model_path}")

model = tf.saved_model.load(model_path)

def process_image(image_path):
    image = cv2.imread(image_path)
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = model(input_tensor)

    detection_scores = detections['detection_scores'].numpy()
    detection_classes = detections['detection_classes'].numpy()
    detection_boxes = detections['detection_boxes'].numpy()

    for i in range(detection_scores.shape[1]):
        if detection_scores[0, i] > 0.5:
            box = detection_boxes[0, i]
            ymin, xmin, ymax, xmax = box

            start_point = (int(xmin * image.shape[1]), int(ymin * image.shape[0]))
            end_point = (int(xmax * image.shape[1]), int(ymax * image.shape[0]))
            color = (0, 255, 0)
            thickness = 2

            image = cv2.rectangle(image, start_point, end_point, color, thickness)

    processed_filename = f'static/uploads/processed_{os.path.basename(image_path)}'
    cv2.imwrite(processed_filename, image)
    return processed_filename