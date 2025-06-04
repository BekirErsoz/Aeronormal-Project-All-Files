from flask import Flask, render_template, request, redirect, url_for
from database import init_db, store_image_data, get_all_images
from image_processing import process_image
from aws import upload_to_s3
import time
import os

app = Flask(__name__)

# AWS S3 bucket name
S3_BUCKET = 'your-s3-bucket-name'

# Veritabanını başlat
init_db()

@app.route('/')
def index():
    images = get_all_images()
    return render_template('index.html', images=images)

@app.route('/capture', methods=['POST'])
def capture():
    # Örnek görüntü dosyasını kullan
    sample_image_path = 'static/sample_image.jpg'
    if os.path.exists(sample_image_path):
        processed_file = process_image(sample_image_path)
        store_image_data(processed_file, time.time())
        upload_to_s3(processed_file, S3_BUCKET)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)