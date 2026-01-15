from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

import json
from werkzeug.utils import secure_filename

# Initialize App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_dev_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///love_plane.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Extensions
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200), default='/static/avatars/default.png')

class Anniversary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

    @property
    def days_count(self):
        today = date.today()
        delta = today - self.date
        return delta.days

class Moment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images_json = db.Column(db.Text, default='[]') # Store images as JSON string

    user = db.relationship('User', backref=db.backref('moments', lazy=True))
    comments = db.relationship('Comment', backref='moment', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='moment', lazy=True, cascade="all, delete-orphan")

    @property
    def images(self):
        return json.loads(self.images_json)

    @images.setter
    def images(self, value):
        self.images_json = json.dumps(value)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', backref=db.backref('messages', lazy=True))

# Routes
@app.route('/')
def index():
    # Only fetch the 5 most recent anniversaries for the main dashboard
    recent_anniversaries = Anniversary.query.order_by(Anniversary.id.desc()).limit(5).all()
    total_count = Anniversary.query.count()
    return render_template('index.html', anniversaries=recent_anniversaries, total_count=total_count)

@app.route('/api/anniversaries')
def get_anniversaries():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    order = request.args.get('order', 'desc')
    
    query = Anniversary.query
    if order == 'asc':
        query = query.order_by(Anniversary.id.asc())
    else:
        query = query.order_by(Anniversary.id.desc())
        
    if per_page == -1:
        # Fetch all items for frontend pagination
        items = [{
            'id': a.id,
            'title': a.title,
            'date': a.date.strftime('%Y-%m-%d'),
            'days_count': a.days_count
        } for a in query.all()]
        
        return {
            'items': items,
            'total_count': len(items)
        }
    else:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = [{
            'id': a.id,
            'title': a.title,
            'date': a.date.strftime('%Y-%m-%d'),
            'days_count': a.days_count
        } for a in pagination.items]
        
        return {
            'items': items,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'current_page': page,
            'total_pages': pagination.pages
        }

@app.route('/anniversaries/add', methods=['POST'])
def add_anniversary():
    title = request.form.get('title')
    date_str = request.form.get('date')
    if title and date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        new_anniversary = Anniversary(title=title, date=date_obj)
        db.session.add(new_anniversary)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/anniversaries/delete/<int:id>')
def delete_anniversary(id):
    anniversary = Anniversary.query.get_or_404(id)
    db.session.delete(anniversary)
    db.session.commit()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/moments')
def moments():
    # Render the moments page. The actual data loading will be done via AJAX to /api/moments
    return render_template('moments.html')

@app.route('/api/moments')
def get_moments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    keyword = request.args.get('keyword', type=str)
    mode = request.args.get('mode', 'fuzzy')
    
    query = Moment.query.order_by(Moment.timestamp.desc())
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if keyword:
        if mode == 'exact':
             query = query.filter(Moment.content == keyword)
        else:
             query = query.filter(Moment.content.like(f'%{keyword}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = []
    for m in pagination.items:
        items.append({
            'id': m.id,
            'content': m.content,
            'images': m.images,
            'publisher': {
                'id': m.user.id,
                'name': m.user.name,
                'avatar': m.user.avatar
            },
            'created_at': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {
                'likes': len(m.likes),
                'comments': len(m.comments)
            },
            # Also include comments/likes detail if needed, but spec just says stats for list
            # We might want to include "is_liked" if we had a current user context
        })
        
    return {
        'code': 200,
        'msg': 'success',
        'data': {
            'items': items,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }

@app.route('/moments/add', methods=['POST'])
def add_moment():
    content = request.form.get('content')
    user_id = request.form.get('user_id', 1, type=int) # Default to user 1
    
    if not content:
        return {'code': 400, 'msg': 'Content is required'}, 400
        
    image_paths = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid collision
                timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp_str}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_paths.append(f"/static/uploads/{filename}")
    
    moment = Moment(content=content, user_id=user_id)
    moment.images = image_paths
    
    db.session.add(moment)
    db.session.commit()
    
    return redirect(url_for('moments'))

@app.route('/moments/<int:id>/delete', methods=['POST'])
def delete_moment(id):
    moment = Moment.query.get_or_404(id)
    db.session.delete(moment)
    db.session.commit()
    return {'code': 200, 'msg': 'success'}

@app.route('/moments/<int:id>/like', methods=['POST'])
def like_moment(id):
    # Toggle like. In a real app we'd check if user already liked.
    # Here we just add a like for the current simulated user.
    user_id = request.json.get('user_id', 1)
    
    existing_like = Like.query.filter_by(user_id=user_id, moment_id=id).first()
    if existing_like:
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        new_like = Like(user_id=user_id, moment_id=id)
        db.session.add(new_like)
        action = 'liked'
        
    db.session.commit()
    return {'code': 200, 'msg': 'success', 'action': action}

@app.route('/moments/<int:id>/comment', methods=['POST'])
def comment_moment(id):
    content = request.json.get('content')
    user_id = request.json.get('user_id', 1)
    
    if not content:
         return {'code': 400, 'msg': 'Content is required'}, 400
         
    comment = Comment(content=content, user_id=user_id, moment_id=id)
    db.session.add(comment)
    db.session.commit()
    
    return {'code': 200, 'msg': 'success', 'data': {
        'id': comment.id,
        'content': comment.content,
        'user': {
            'name': comment.user.name,
            'avatar': comment.user.avatar
        },
        'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }}

@app.route('/api/moments/<int:id>/comments')
def get_moment_comments(id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Comment.query.filter_by(moment_id=id)\
        .order_by(Comment.timestamp.asc())\
        .paginate(page=page, per_page=per_page, error_out=False)
        
    items = [{
        'id': c.id,
        'content': c.content,
        'user': {
            'name': c.user.name,
            'avatar': c.user.avatar
        },
        'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for c in pagination.items]
    
    return {
        'code': 200, 
        'msg': 'success', 
        'data': {
            'items': items,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat/history')
def get_chat_history():
    before_id = request.args.get('before_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    query = Message.query.order_by(Message.timestamp.desc())
    
    if before_id:
        query = query.filter(Message.id < before_id)
        
    messages = query.limit(limit).all()
    # Return in reverse order (oldest first) so frontend can append easily, 
    # or keep desc and frontend prepends.
    # The doc example shows a list. Let's return desc (newest first) as queried, 
    # and frontend handles display order (usually flex-direction: column-reverse or prepend).
    
    items = [{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_name': m.sender.name,
        'sender_avatar': m.sender.avatar
    } for m in messages]
    
    return {
        'items': items,
        'has_more': len(items) == limit
    }

# Socket.IO Events
@socketio.on('join')
def on_join(data):
    room = data.get('room', 'couple_room')
    join_room(room)
    # emit('status', {'msg': 'Someone joined'}, room=room)

@socketio.on('message')
def on_message(data):
    content = data.get('content')
    sender_id = data.get('sender_id', 1)
    room = data.get('room', 'couple_room')
    
    if not content:
        return
        
    # Save to DB
    msg = Message(content=content, sender_id=sender_id)
    db.session.add(msg)
    db.session.commit()
    
    # Broadcast
    # Note: In a real app we might want to reload the object to get sender relationship,
    # but here we can just use what we have or query.
    # To get sender name/avatar, we need the user object.
    # Since we just added it, it's in session, but we might need to refresh or query User.
    user = User.query.get(sender_id)
    
    emit('response', {
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_name': user.name if user else 'Unknown',
        'sender_avatar': user.avatar if user else ''
    }, room=room)

@socketio.on('typing')
def on_typing(data):
    room = data.get('room', 'couple_room')
    emit('status_change', {'user_id': data.get('sender_id'), 'status': 'typing'}, room=room, include_self=False)

@socketio.on('stop_typing')
def on_stop_typing(data):
    room = data.get('room', 'couple_room')
    emit('status_change', {'user_id': data.get('sender_id'), 'status': 'online'}, room=room, include_self=False)

@socketio.on('recall')
def on_recall(data):
    msg_id = data.get('id')
    sender_id = data.get('sender_id')
    room = data.get('room', 'couple_room')
    
    msg = Message.query.get(msg_id)
    if msg and msg.sender_id == sender_id:
        db.session.delete(msg)
        db.session.commit()
        emit('message_recalled', {'id': msg_id}, room=room)

# Run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
