import threading
import hashlib
import json
from time import time
from uuid import uuid4
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from flask import Flask, jsonify, request
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
import tkinter as tk
from tkinter import scrolledtext

# Blockchain Class Definition
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(previous_hash='1', proof=100)
        self.model = self.train_ai_model()  # Yapay zeka modelini başlatıyoruz

    def create_block(self, proof, previous_hash=None):
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

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Yapay Zeka Modeli Eğitimi
    def train_ai_model(self):
        # Basit bir yapay zeka modeli: Logistic Regression
        X = np.array([[random.random() for _ in range(3)] for _ in range(100)])
        y = np.array([random.choice([0, 1]) for _ in range(100)])
        model = LogisticRegression()
        model.fit(X, y)
        return model

    # Yeni veriyi analiz etme
    def analyze_data(self, data):
        prediction = self.model.predict([data])
        return prediction[0]

# Flask Web Application
app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient="drone_id_123",
        amount=1,
    )

    block = blockchain.create_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    values = request.get_json()
    if 'data' not in values:
        return 'Missing data', 400

    # Yapay zeka ile veriyi analiz et
    prediction = blockchain.analyze_data(values['data'])
    response = {'prediction': int(prediction)}
    return jsonify(response), 200

# Flask Uygulamasını Ayrı Bir Thread'de Başlatma
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Tkinter GUI Uygulaması
def start_gui():
    root = tk.Tk()
    root.title("Blockchain Uygulaması")

    # Text area for output
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
    text_area.grid(column=0, pady=10, padx=10)

    def mine_block():
        response = app.test_client().get('/mine')
        text_area.insert(tk.END, f"Mine Block: {response.json['message']}\n")

    def show_chain():
        response = app.test_client().get('/chain')
        text_area.insert(tk.END, f"Blockchain:\n{json.dumps(response.json, indent=2)}\n")

    # Buttons
    mine_button = tk.Button(root, text="Mine Block", command=mine_block)
    mine_button.grid(column=0, row=1, pady=5)

    chain_button = tk.Button(root, text="Show Chain", command=show_chain)
    chain_button.grid(column=0, row=2, pady=5)

    root.mainloop()

# Flask'i arka planda başlat
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Tkinter GUI'yi başlat
start_gui()