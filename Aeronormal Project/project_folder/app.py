from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from database import init_db, store_image_data, get_all_images
from image_processing import process_image
from aws import upload_to_s3
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# AWS S3 bucket name
S3_BUCKET = 'your-s3-bucket-name'

# Veritabanını başlat
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        processed_file = process_image(filepath)
        store_image_data(processed_file, time.time())
        upload_to_s3(processed_file, S3_BUCKET)
        return redirect(url_for('index'))

@app.route('/get_images')
def get_images():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    images = get_all_images()
    total_images = len(images)
    images = images[(page - 1) * per_page: page * per_page]
    image_data = [{
        'filename': url_for('static', filename=f'uploads/{os.path.basename(image.filename)}'),
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