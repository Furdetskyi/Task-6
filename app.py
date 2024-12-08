from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restful import Api
from blocklist import BLOCKLIST
from resources.user import blp as UserBlueprint
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)

# Конфігурація для SQLAlchemy та JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://root:Valikf2005@34.79.21.6:5432/test'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "12345"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Термін дії токену (секунди)

# Ініціалізація компонентів
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Модель користувача
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # У реальному проекті шифруйте паролі!

    def __repr__(self):
        return f"<User {self.username}>"

# Модель продукту
class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id', ondelete='CASCADE'))  # Каскадне видалення
    user = db.relationship('UserModel', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"<Product {self.name}>"

# Створення всіх таблиць в базі даних
with app.app_context():
    db.create_all()

# Логін та отримання токена
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = UserModel.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:  # Простий приклад перевірки
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Створення користувача
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = UserModel(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully"}), 201

# Отримання користувача за ID (захищено)
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    return jsonify({"id": user.id, "username": user.username, "password": user.password})

# Оновлення користувача (захищено)
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data['username']
    user.password = data['password']
    db.session.commit()
    return jsonify({"message": "User updated successfully"})

# Отримання всіх користувачів (захищено)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = UserModel.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify({"users": users_list})

# Видалення користувача (захищено)
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})

# Створення продукту (захищено)
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_product = ProductModel(
        name=data['name'], 
        brand=data['brand'], 
        price=data['price'], 
        user_id=current_user_id
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

# Отримання продукту за ID (захищено)
@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price
    })

# Оновлення продукту (захищено)
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data['name']
    product.brand = data['brand']
    product.price = data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

# Отримання всіх продуктів (захищено)
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = ProductModel.query.all()
    products_list = [{"id": product.id, "name": product.name, "brand": product.brand, "price": product.price} for product in products]
    return jsonify({"products": products_list})

# Видалення продукту (захищено)
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})

# Запуск додатку
if __name__ == "__main__":
    app.run(debug=True)