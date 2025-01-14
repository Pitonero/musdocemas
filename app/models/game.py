# app/models/game.py
from ..models import db

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    team_1_score = db.Column(db.Integer, default=0)
    team_2_score = db.Column(db.Integer, default=0)
    round_number = db.Column(db.Integer, default=1)

    # Relación con la sala de espera
    room = db.relationship('Room', backref=db.backref('games', lazy=True))
