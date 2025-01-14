# tests.py
import unittest
from app import app, db, socketio
from app.game_logic import MusGame
from app.models import User

class MusGameTest(unittest.TestCase):
    def setUp(self):
        self.game = MusGame()

    def test_add_player(self):
        self.assertTrue(self.game.add_player(1))
        self.assertTrue(self.game.add_player(2))
        self.assertFalse(self.game.add_player(5))  # Debería fallar si hay 4 jugadores

    def test_process_move(self):
        self.game.add_player(1)
        self.game.add_player(2)
        self.game.start_round()
        result = self.game.process_move(1, "mus")
        self.assertEqual(result, None)  # Debería procesar correctamente el movimiento

class AuthTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_login(self):
        # Probar inicio de sesión y token JWT
        response = self.app.post('/login', json={"username": "test_user", "password": "test_password"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
