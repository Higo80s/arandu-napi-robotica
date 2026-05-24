import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import User
import unittest

class TestPasswordPolicy(unittest.TestCase):
    def setUp(self):
        self.user = User(email='test@example.com', nome='Test User')

    def test_weak_password_length(self):
        with self.assertRaises(ValueError) as cm:
            self.user.set_password("Short1!")
        self.assertIn("mínimo 12 caracteres", str(cm.exception))

    def test_missing_uppercase(self):
        with self.assertRaises(ValueError) as cm:
            self.user.set_password("longpassword1!")
        self.assertIn("letra maiúscula", str(cm.exception))

    def test_missing_number(self):
        with self.assertRaises(ValueError) as cm:
            self.user.set_password("LongPassword!")
        self.assertIn("número", str(cm.exception))

    def test_missing_special(self):
        with self.assertRaises(ValueError) as cm:
            self.user.set_password("LongPassword1")
        self.assertIn("caractere especial", str(cm.exception))

    def test_strong_password(self):
        try:
            self.user.set_password("StrongPass123!@#")
        except ValueError:
            self.fail("set_password raised ValueError unexpectedly!")
        self.assertTrue(self.user.check_password("StrongPass123!@#"))

if __name__ == '__main__':
    unittest.main()
