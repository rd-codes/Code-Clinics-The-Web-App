from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2 import service_account
import hashlib

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///code_clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_volunteer = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    volunteer_slots = db.relationship('VolunteerSlot', backref='volunteer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('volunteer_slot.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VolunteerSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    booking = db.relationship('Booking', backref='slot', uselist=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_calendar_service():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_volunteer = request.form.get('is_volunteer') == 'on'
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(email=email, name=name, is_volunteer=is_volunteer)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/slots', methods=['GET'])
@login_required
def get_slots():
    slots = VolunteerSlot.query.filter_by(is_available=True).all()
    return jsonify([{
        'id': slot.id,
        'title': f'{slot.subject} with {slot.volunteer.name}',
        'start': slot.start_time.isoformat(),
        'end': slot.end_time.isoformat(),
        'volunteer_name': slot.volunteer.name,
        'subject': slot.subject
    } for slot in slots])

@app.route('/api/book', methods=['POST'])
@login_required
def book_slot():
    slot_id = request.json.get('slot_id')
    slot = VolunteerSlot.query.get_or_404(slot_id)
    
    if not slot.is_available:
        return jsonify({'error': 'Slot is not available'}), 400
        
    # Check if the user is trying to book their own volunteer slot
    if slot.volunteer_id == current_user.id:
        return jsonify({'error': 'You cannot book your own volunteer slot'}), 400
        
    booking = Booking(user_id=current_user.id, slot_id=slot_id)
    slot.is_available = False
    
    # Add to Google Calendar
    service = get_calendar_service()
    event = {
        'summary': f'Code Clinic Session with {slot.volunteer.name}',
        'description': f'One-on-one coding session with {slot.volunteer.name}',
        'start': {
            'dateTime': slot.start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': slot.end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': current_user.email},
            {'email': slot.volunteer.email}
        ],
    }
    
    try:
        service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        print(f"Error adding to Google Calendar: {e}")
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking successful'})

@app.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': booking.id,
        'start_time': booking.slot.start_time.isoformat(),
        'end_time': booking.slot.end_time.isoformat(),
        'volunteer_name': booking.slot.volunteer.name,
        'subject': booking.slot.subject
    } for booking in bookings])

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    slot = booking.slot
    slot.is_available = True
    
    # Remove from Google Calendar
    service = get_calendar_service()
    try:
        events = service.events().list(
            calendarId='primary',
            timeMin=slot.start_time.isoformat() + 'Z',
            timeMax=slot.end_time.isoformat() + 'Z',
            q=f'Code Clinic Session with {slot.volunteer.name}'
        ).execute()
        
        for event in events.get('items', []):
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
    except Exception as e:
        print(f"Error removing from Google Calendar: {e}")
    
    db.session.delete(booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled successfully'})

@app.route('/api/volunteer/slots', methods=['POST'])
@login_required
def add_volunteer_slot():
    if not current_user.is_volunteer:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time'])
    subject = data.get('subject', '').strip()
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    slot = VolunteerSlot(
        volunteer_id=current_user.id,
        start_time=start_time,
        end_time=end_time,
        subject=subject
    )
    
    db.session.add(slot)
    db.session.commit()
    
    return jsonify({'message': 'Slot added successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 