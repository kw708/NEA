#integration 
import os
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

#from flask import Flask, request, redirect, url_for, flash, render_template
#from flask_mail import Mail, Message
#from werkzeug.security import generate_password_hash, check_password_hash
#import random
#import string

# Load environment variables
load_dotenv()

# App Configurations
basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///' + os.path.join(basedir, 'users.db') #'sqlite:///users.db'

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL_PROTOCOL', 'sqlite:///') + os.path.join(basedir, os.getenv('DATABASE_URL_FILE_NAME'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False) #user is default also email
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Create database tables
with app.app_context():
    db.create_all()

# Home Route
@app.route('/')
def home():
    render_template('index.html')
    

# Authentication Routes
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Validate input
    if not data or not data.name.get('name') not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 409
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create session for new user
        session['user_id'] = new_user.id
        
        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        # Create session
        session['user_id'] = user.id
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    # Clear session
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Fetch user details
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200

@app.route('/is_authenticated', methods=['GET'])
def is_authenticated():
    return jsonify({
        "authenticated": 'user_id' in session
    }), 200

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500



if __name__ == '__main__':
    app.run(debug=True)
