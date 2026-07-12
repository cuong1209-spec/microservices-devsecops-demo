import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
PORT = 5000

# HARDCODED SECRET - VULNERABILITY FOR DEMO PURPOSES ONLY
# Critical Security Vulnerability (CWE-798): Hardcoded credentials
# This simulates a developer accidentally committing credentials.
# Gitleaks in the CI/CD pipeline will flag this pattern.
STRIPE_API_KEY = "sk_live_51Habc1234567890123456789"

orders = [
    {"id": 101, "product_id": 1, "quantity": 1, "status": "Pending"},
    {"id": 102, "product_id": 2, "quantity": 5, "status": "Shipped"}
]

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    # Query product service to check if product exists (service-to-service communication)
    product_url = f"http://product-service:3000/api/products/{data['product_id']}"
    try:
        response = requests.get(product_url, timeout=5)
        if response.status_code != 200:
            return jsonify({"error": "Product does not exist"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to contact Product Service: {str(e)}"}), 500

    new_order = {
        "id": len(orders) + 101,
        "product_id": data['product_id'],
        "quantity": data['quantity'],
        "status": "Created"
    }
    orders.append(new_order)
    return jsonify(new_order), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
