from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import hashlib
import json
from time import time
from uuid import uuid4
import requests
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc or parsed_url.path)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof'], self.hash(last_block)):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/api/full-chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

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

    def new_transaction(self, sender, recipient, certificate):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'certificate': certificate,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while not self.valid_proof(last_proof, proof, last_hash):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)
CORS(app)

node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/')
@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/institution')
def issue_page():
    return render_template('institution.html')

@app.route('/verifier')
def verify_page():
    return render_template('verifier.html')

@app.route('/blockchain')
def blockchain_page():
    return render_template('blockchain.html')

@app.route('/api/issue', methods=['POST'])
def issue_certificate():
    data = request.json
    required = ['sender', 'recipient', 'certificate_id', 'course', 'date_issued']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400

    certificate = {
        'id': data['certificate_id'],
        'course': data['course'],
        'date_issued': data['date_issued']
    }

    blockchain.new_transaction(data['sender'], data['recipient'], certificate)
    proof = blockchain.proof_of_work(blockchain.last_block)
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof, previous_hash)

    return jsonify({
        'message': f'Certificate has been added to Block {block["index"]}',
        'block': block
    }), 201

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse

# -------------------- Blockchain Class --------------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc or parsed_url.path)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof'], self.hash(last_block)):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/api/full-chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

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

    def new_transaction(self, sender, recipient, certificate):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'certificate': certificate,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while not self.valid_proof(last_proof, proof, last_hash):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# -------------------- Flask Setup --------------------
app = Flask(__name__)
CORS(app)

node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# -------------------- HTML ROUTES --------------------
@app.route('/')
@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/institution')
def issue_page():
    return render_template('institution.html')

@app.route('/verifier')
def verify_page():
    return render_template('verifier.html')

@app.route('/blockchain')
def blockchain_page():
    return render_template('blockchain.html')

# -------------------- API ROUTES --------------------
@app.route('/api/issue', methods=['POST'])
def issue_certificate():
    data = request.json
    required = ['sender', 'recipient', 'certificate_id', 'course', 'date_issued']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400

    certificate = {
        'id': data['certificate_id'],
        'course': data['course'],
        'date_issued': data['date_issued']
    }

    blockchain.new_transaction(data['sender'], data['recipient'], certificate)
    proof = blockchain.proof_of_work(blockchain.last_block)
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof, previous_hash)

    return jsonify({
        'message': f'Certificate has been added to Block {block["index"]}',
        'block': block
    }), 201

@app.route('/api/verify', methods=['GET'])
def verify_certificate():
    cert_id = request.args.get("id")
    if not cert_id:
        return jsonify({'error': 'Missing certificate ID'}), 400

    for block in blockchain.chain:
        for tx in block['transactions']:
            cert = tx.get('certificate', {})
            if cert.get('id') == cert_id:
                return jsonify({
                    'valid': True,
                    'block_index': block['index'],
                    'transaction': tx
                }), 200

    return jsonify({'valid': False, 'message': 'Certificate not found'}), 404

@app.route('/api/full-chain', methods=['GET'])
def get_full_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }), 200

# -------------------- Run the App --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/api/full-chain', methods=['GET'])
def get_full_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }), 200

# -------------------- Run the App --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
