from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import json
import os

app = Flask(__name__)

# Конфігурація JWT
app.config["JWT_SECRET_KEY"] = "12345"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Термін дії токену (секунди)
jwt = JWTManager(app)

# Файли для зберігання даних
USERS_FILE = "users.json"
PRODUCTS_FILE = "products.json"

# Функції роботи з файлами
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Маршрути для користувачів
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    users = load_data(USERS_FILE)
    user = next((u for u in users if u['username'] == data['username'] and u['password'] == data['password']), None)
    if user:
        access_token = create_access_token(identity=user['id'])
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    users = load_data(USERS_FILE)
    user_id = len(users) + 1
    new_user = {"id": user_id, "username": data['username'], "password": data['password']}
    users.append(new_user)
    save_data(USERS_FILE, users)
    return jsonify({"message": "User added successfully"}), 201

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = load_data(USERS_FILE)
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    users = load_data(USERS_FILE)
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404

# Маршрути для продуктів
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    products = load_data(PRODUCTS_FILE)
    product_id = len(products) + 1
    new_product = {
        "id": product_id,
        "name": data['name'],
        "brand": data['brand'],
        "price": data['price'],
        "user_id": current_user_id
    }
    products.append(new_product)
    save_data(PRODUCTS_FILE, products)
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = load_data(PRODUCTS_FILE)
    return jsonify(products)

@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    products = load_data(PRODUCTS_FILE)
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"message": "Product not found"}), 404

# Запуск додатку
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Встановлюємо порт зі змінної середовища або стандартний
    app.run(host="0.0.0.0", port=port)
