import os
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename

# App configuration
app = Flask(__name__)

# Azure SQL Database connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://<username>:<password>@<servername>.database.windows.net/<databasename>?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for JWT
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to store uploaded videos
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}  # Allowed video formats

# Initialize the database
db = SQLAlchemy(app)
CORS(app)

# Models for User and Video
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # consumer or creator

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    video_path = db.Column(db.String(100), nullable=False)
    hashtags = db.Column(db.String(100), nullable=True)

    # Add to_dict method for JSON serialization
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "video_path": self.video_path,
            "hashtags": self.hashtags
        }

# JWT token generation function
def generate_jwt(user):
    payload = {
        'username': user.username,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# JWT token validation decorator
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

# Route for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == password:  # Simplified, consider using hashed passwords in production
        token = generate_jwt(user)
        return jsonify({'success': True, 'token': token})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route for sign-up
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if role not in ['consumer', 'creator']:
        return jsonify({'message': 'Role must be either consumer or creator.'}), 400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'User already exists.'}), 400
    
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully.'}), 201

# Route to upload a video
@app.route('/upload', methods=['POST'])
@token_required
def upload_video(current_user):
    if current_user.role != 'creator':
        return jsonify({'message': 'Permission denied! You need to be a creator to upload videos.'}), 403

    # Handle video file upload
    video_file = request.files['video']
    if video_file and allowed_file(video_file.filename):
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)

        # Generate thumbnail
        thumbnail = generate_thumbnail(video_path)

        # Save video info to database
        video = Video(title=request.form['title'], description=request.form['description'], 
                      thumbnail=thumbnail, video_path=video_path, hashtags=request.form['hashtags'])
        db.session.add(video)
        db.session.commit()

        return jsonify({'message': 'Video uploaded successfully!'})

    return jsonify({'message': 'Invalid file format.'}), 400

# Route for searching videos (Now from the DB instead of Elasticsearch)
@app.route('/search', methods=['GET'])
def search_videos():
    query = request.args.get('q')
    videos = Video.query.filter(
        Video.title.like(f'%{query}%') | 
        Video.description.like(f'%{query}%') |
        Video.hashtags.like(f'%{query}%')
    ).all()
    
    return jsonify([video.to_dict() for video in videos])

@app.route('/videos', methods=['GET'])
def get_videos():
    videos = Video.query.all()
    return jsonify([video.to_dict() for video in videos])

@app.route('/')
def index():
    return "Hello, Flask! The server is running."

# Helper functions for video upload
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_thumbnail(video_path):
    thumbnail_path = video_path + '.jpg'
    command = f"ffmpeg -i {video_path} -ss 00:00:01.000 -vframes 1 {thumbnail_path}"
    os.system(command)  # In production, consider using a background task system (e.g., Celery)
    return thumbnail_path

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
