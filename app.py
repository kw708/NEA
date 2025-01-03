from flask import Flask, request, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

app = Flask(__name__)

# App Configurations
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

db = SQLAlchemy(app)
mail = Mail(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)

# Home Route
@app.route('/')
def home():
    return 'Welcome to the Home Page!'

# Sign-Up Route
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

#password length validation
    if len(password) < 8 :
        return "password is too short"
    

    # Hash the password for security
    hashed_password = generate_password_hash(password, method='sha256')

    # Save user to the database
    user = User(name=name, email=email, password=hashed_password, verified=False)
    db.session.add(user)
    db.session.commit()

    # Send a confirmation email
    send_confirmation_email(email)

    flash('Sign-up successful! A confirmation email has been sent to your email address.', 'success')
    return redirect(url_for('home'))

# Send Confirmation Email
def send_confirmation_email(email):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    confirmation_url = f'http://127.0.0.1:5000/confirm/{token}'

    # Store token temporarily 
    app.config['CONFIRMATION_TOKENS'] = {email: token}

    msg = Message('Confirm Your Email', sender='your_email@gmail.com', recipients=[email])
    msg.body = f'Click the link to confirm your email: {confirmation_url}'
    mail.send(msg)

# Email Confirmation Route
@app.route('/confirm/<token>')
def confirm_email(token):
    confirmation_tokens = app.config.get('CONFIRMATION_TOKENS', {})
    email = next((key for key, value in confirmation_tokens.items() if value == token), None)

    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash('Your email has been confirmed!', 'success')
        else:
            flash('User not found.', 'danger')
    else:
        flash('Invalid or expired token.', 'danger')

    return redirect(url_for('home'))

# Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        if user.verified:
            flash('Login successful!', 'success')
        else:
            flash('Please confirm your email before logging in.', 'danger')
    else:
        flash('Invalid credentials.', 'danger')

    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
