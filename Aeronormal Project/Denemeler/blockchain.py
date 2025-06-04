from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import json
import hashlib
from time import time
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'txt'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Blockchain setup
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

blockchain = Blockchain()

def add_to_blockchain(data):
    blockchain.new_transaction(sender="app", recipient="user", amount=1)
    blockchain.new_block(proof=12345)
    with open("blockchain.json", "w") as file:
        json.dump(blockchain.chain, file)

# Database setup
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    data = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

def store_data(filename, data):
    new_data = Data(filename=filename, timestamp=time(), data=json.dumps(data))
    db.session.add(new_data)
    db.session.commit()

def get_all_data():
    return Data.query.all()

# Flask routes
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Management System</title>
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        h1 { text-align: center; margin-bottom: 20px; }
        form { margin-bottom: 20px; }
        .btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background-color: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Management System</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit" class="btn">Upload and Process Data</button>
        </form>
        <h2>Processed Data</h2>
        <div id="data-table"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script>
        $(document).ready(function() {
            fetch('/get_data').then(response => response.json()).then(data => {
                let table = '<table><tr><th>ID</th><th>Filename</th><th>Timestamp</th><th>Data</th></tr>';
                data.forEach(row => {
                    table += `<tr><td>${row.id}</td><td>${row.filename}</td><td>${row.timestamp}</td><td>${row.data}</td></tr>`;
                });
                table += '</table>';
                $('#data-table').html(table);
            });
        });
    </script>
</body>
</html>
    """)

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
        data = process_data(filepath)
        store_data(filename, data)
        add_to_blockchain(data)
        return redirect(url_for('index'))

@app.route('/get_data')
def get_data():
    data_records = get_all_data()
    data_list = [{
        'id': record.id,
        'filename': record.filename,
        'timestamp': record.timestamp,
        'data': record.data
    } for record in data_records]
    return jsonify(data_list)

def process_data(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        df = pd.read_csv(filepath)
    elif ext == 'txt':
        df = pd.read_csv(filepath, delimiter='\t')
    return df.to_dict()

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)