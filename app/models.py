# This file defines the database models for the application using SQLAlchemy.
# app/models.py  
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registrations = db.relationship('Registration', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    registrations = db.relationship('Registration', back_populates='event', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Event {self.name}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='registrations')
    event = db.relationship('Event', back_populates='registrations')

    def __repr__(self):
        return f'<Registration User:{self.user_id} Event:{self.event_id}>'