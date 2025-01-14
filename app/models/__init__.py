# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# Crear una única instancia de SQLAlchemy
db = SQLAlchemy()

def initialize_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Importar y exponer modelos si es necesario
from .user import User
from .room import Room
from .game import Game

