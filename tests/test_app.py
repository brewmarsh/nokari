import unittest
import json
from backend.app import app, db
from backend.models import User, Resume, CoverLetter

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        response = self.app.post('/users',
                                 data=json.dumps({'email': 'test@example.com', 'role': 'user'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'test@example.com')

    def test_create_resume(self):
        user = User(email='test@example.com', role='user')
        db.session.add(user)
        db.session.commit()

        response = self.app.post('/resumes',
                                 data=json.dumps({'name': 'test_resume', 'file': 'resumes/test.pdf', 'user_id': user.id}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'test_resume')

    def test_create_cover_letter(self):
        user = User(email='test@example.com', role='user')
        db.session.add(user)
        db.session.commit()

        response = self.app.post('/cover-letters',
                                 data=json.dumps({'name': 'test_cover_letter', 'file': 'cover_letters/test.pdf', 'user_id': user.id}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'test_cover_letter')

if __name__ == '__main__':
    unittest.main()
