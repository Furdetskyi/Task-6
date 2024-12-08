from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from passlib.hash import pbkdf2_sha256
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

# Оголошення Blueprint для операцій з користувачами
blp = Blueprint("Users", "users", description="User operations")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        # Перевірка правильності пароля
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Створення токенів
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        # Якщо користувач не знайдений або пароль неправильний
        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # Отримуємо ID токена
        jti = get_jwt()["jti"]
        # Додаємо його в блокліст
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        # Отримуємо поточного користувача
        current_user = get_jwt_identity()
        # Генеруємо новий токен
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
    
    