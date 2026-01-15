import unittest
import json
import os
from datetime import datetime

# Use memory DB for tests
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from app import app, db, User, Message, socketio

class ChatTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create user
            u = User(name='Boy', id=1)
            db.session.add(u)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_history_empty(self):
        rv = self.app.get('/api/chat/history')
        data = json.loads(rv.data)
        self.assertEqual(len(data['items']), 0)

    def test_send_and_receive_socket(self):
        # SocketIO test client
        client = socketio.test_client(app)
        client.emit('join', {'room': 'couple_room'})
        
        # Send message
        client.emit('message', {
            'content': 'Hello Love',
            'sender_id': 1,
            'room': 'couple_room'
        })
        
        # Check received response
        received = client.get_received()
        # Filter for 'response' event. Note: get_received returns all events since last call
        responses = [evt for evt in received if evt['name'] == 'response']
        self.assertTrue(len(responses) > 0)
        data = responses[0]['args'][0]
        self.assertEqual(data['content'], 'Hello Love')
        self.assertEqual(data['sender_id'], 1)
        
        # Check DB
        with app.app_context():
            self.assertEqual(Message.query.count(), 1)
            msg = Message.query.first()
            self.assertEqual(msg.content, 'Hello Love')

    def test_typing_status(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        client1.emit('join', {'room': 'couple_room'})
        client2.emit('join', {'room': 'couple_room'})
        
        # Client 1 types
        client1.emit('typing', {'sender_id': 1, 'room': 'couple_room'})
        
        # Client 2 should receive
        received = client2.get_received()
        status_evts = [evt for evt in received if evt['name'] == 'status_change']
        self.assertTrue(len(status_evts) > 0)
        self.assertEqual(status_evts[0]['args'][0]['status'], 'typing')

    def test_recall_message(self):
        # Manually add message
        with app.app_context():
            m = Message(content='Wrong', sender_id=1)
            db.session.add(m)
            db.session.commit()
            msg_id = m.id
            
        client = socketio.test_client(app)
        client.emit('join', {'room': 'couple_room'})
        
        client.emit('recall', {'id': msg_id, 'sender_id': 1, 'room': 'couple_room'})
        
        # Check DB
        with app.app_context():
            self.assertIsNone(Message.query.get(msg_id))
            
        # Check broadcast
        received = client.get_received()
        recall_evts = [evt for evt in received if evt['name'] == 'message_recalled']
        self.assertTrue(len(recall_evts) > 0)
        self.assertEqual(recall_evts[0]['args'][0]['id'], msg_id)

if __name__ == '__main__':
    unittest.main()
