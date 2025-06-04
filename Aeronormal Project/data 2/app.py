from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import init_db, store_image_data, get_all_images
from image_processing import process_image
from aws import upload_to_s3
import os

app = Flask(__name__)

# AWS S3 bucket name
S3_BUCKET = 'your-s3-bucket-name'

# Veritabanını başlat
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    sample_image_path = 'static/images/sample_image.jpg'
    if os.path.exists(sample_image_path):
        processed_file = process_image(sample_image_path)
        store_image_data(processed_file, time.time())
        upload_to_s3(processed_file, S3_BUCKET)
    return '', 204

@app.route('/get_images')
def get_images():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    images = get_all_images()
    total_images = len(images)
    images = images[(page - 1) * per_page: page * per_page]
    image_data = [{
        'filename': url_for('static', filename=f'images/{os.path.basename(image.filename)}'),
        'timestamp': image.timestamp
    } for image in images]
    return jsonify(image_data)

@app.route('/total_pages')
def total_pages():
    per_page = 9
    images = get_all_images()
    total_images = len(images)
    total_pages = (total_images + per_page - 1) // per_page
    return jsonify({'total_pages': total_pages})

if __name__ == '__main__':
    app.run(debug=True)