import os
os.environ["FLASK_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from app import create_app
from models.models import db, Task, User, ActivityLog

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.user = User(id="test-user-id", name="Test User", email="test@example.com")
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])

if __name__ == "__main__":
    unittest.main()
