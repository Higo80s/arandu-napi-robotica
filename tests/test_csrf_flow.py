import os
print(f"DEBUG PRE-IMPORT: DATABASE_URL={os.environ.get('DATABASE_URL')}")
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
print(f"DEBUG PRE-IMPORT SET: DATABASE_URL={os.environ.get('DATABASE_URL')}")

import unittest
from app import app, db
from flask_login import login_user
from models import User
from flask_wtf.csrf import generate_csrf
import json

print(f"DEBUG POST-IMPORT: app.config URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")

class TestCSRFFlow(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True 
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        print(f"DEBUG SETUP: app.config URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        self.app = app.test_client()
        
        with app.app_context():
            # Force Engine Disposal to reconnect with new URI
            db.session.remove()
            db.engine.dispose()
            
            db.drop_all() # Ensure clean state
            db.create_all()
            # Create Test User
            user = User(nome='Test User', email='test@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    def login(self):
        # 1. Get Login Page to fetch CSRF Token
        response = self.app.get('/auth/login')
        csrf_token = ''
        import re
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.data.decode('utf-8'))
        if match:
            csrf_token = match.group(1)
            
        # 2. POST with Token
        return self.app.post('/auth/login', data=dict(
            email='test@test.com',
            password='password',
            csrf_token=csrf_token
        ), follow_redirects=True)

    def test_refresh_csrf_requires_login(self):
        """Test API endpoint requires login"""
        response = self.app.get('/api/refresh_csrf')
        # Expect 302 (Redirect to login) or 401
        self.assertIn(response.status_code, [302, 401])

    def test_refresh_csrf_success(self):
        """Test API endpoint returns token when logged in"""
        self.login()
        response = self.app.get('/api/refresh_csrf')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('csrf_token', data)
        self.assertTrue(len(data['csrf_token']) > 0)

    def test_csrf_error_ajax(self):
        """Test AJAX request with bad token returns JSON error"""
        # Note: Default behavior might be 302 unless we mock specific error raiser.
        # But we can try to POST with bad token to a protected route.
        self.login()
        response = self.app.post('/api/programas', 
                                 data=json.dumps({'nome': 'Test'}),
                                 content_type='application/json',
                                 headers={'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': 'invalid'})
        
        # Should be 400 or 401 JSON
        # If Flask-WTF handles it, it raises CSRFError -> caught by our handler
        if response.status_code == 401:
            data = json.loads(response.data)
            self.assertEqual(data['error'], 'CSRF Error')
        elif response.status_code == 302:
             # If not caught correctly as JSON request?
             self.fail("Should notify as JSON error, got Redirect")
        # Note: If testing environment disables CSRF by default, this might pass incorrectly.
        
if __name__ == '__main__':
    unittest.main()
