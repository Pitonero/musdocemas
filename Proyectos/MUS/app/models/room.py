# app/models/room.py
from ..models import db

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    player_count = db.Column(db.Integer, default=0)
    game_in_progress = db.Column(db.Boolean, default=False)
