# auth.py - Módulo para autenticación segura con JWT
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, Blueprint
from app.models import User, db  # Ahora importamos User y db desde app.models
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)  # Definimos el blueprint aquí
SECRET_KEY = "your_secret_key"

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
    

def generate_token(user_id):
    """Genera un token JWT para el usuario."""
    token_data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY)
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/protected', methods=['GET'])
def protected_route():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token requerido"}), 403
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"message": "Acceso concedido", "user_id": decoded["user_id"]})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 403

