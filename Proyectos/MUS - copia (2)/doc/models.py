# models.py
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100))
    games_played = db.Column(db.Integer, default=0)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    player_count = db.Column(db.Integer, default=0)
    game_in_progress = db.Column(db.Boolean, default=False)
