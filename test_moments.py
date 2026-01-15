import unittest
import json
import os

# Set test database before importing app
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from app import app, db, User, Moment

class MomentsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        # Ensure we are using memory db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create user
            u = User(name='TestUser')
            db.session.add(u)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_moments_empty(self):
        # Since setUp creates a user, but no moments
        rv = self.app.get('/api/moments')
        data = json.loads(rv.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(len(data['data']['items']), 0)

    def test_add_moment(self):
        rv = self.app.post('/moments/add', data=dict(
            content='Hello World',
            user_id=1
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        
        # Check if added
        with app.app_context():
            self.assertEqual(Moment.query.count(), 1)
            m = Moment.query.first()
            self.assertEqual(m.content, 'Hello World')

    def test_get_moments_list(self):
        # Add a moment first
        self.app.post('/moments/add', data=dict(content='Test Content', user_id=1))
        
        rv = self.app.get('/api/moments')
        data = json.loads(rv.data)
        self.assertEqual(len(data['data']['items']), 1)
        self.assertEqual(data['data']['items'][0]['content'], 'Test Content')
        self.assertEqual(data['data']['items'][0]['publisher']['name'], 'TestUser')

    def test_like_moment(self):
        self.app.post('/moments/add', data=dict(content='Like Me', user_id=1))
        
        # Like
        rv = self.app.post('/moments/1/like', json={'user_id': 1})
        data = json.loads(rv.data)
        self.assertEqual(data['action'], 'liked')
        
        # Unlike
        rv = self.app.post('/moments/1/like', json={'user_id': 1})
        data = json.loads(rv.data)
        self.assertEqual(data['action'], 'unliked')

    def test_comment_moment(self):
        self.app.post('/moments/add', data=dict(content='Comment Me', user_id=1))
        
        # Add comment
        rv = self.app.post('/moments/1/comment', json={'content': 'Nice!', 'user_id': 1})
        data = json.loads(rv.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['content'], 'Nice!')

        # Get comments list
        rv = self.app.get('/api/moments/1/comments')
        data = json.loads(rv.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(len(data['data']['items']), 1)
        self.assertEqual(data['data']['items'][0]['content'], 'Nice!')
        self.assertEqual(data['data']['items'][0]['user']['name'], 'TestUser')

if __name__ == '__main__':
    unittest.main()