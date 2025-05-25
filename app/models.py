from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    registrations = db.relationship('Registration', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def is_registered_for(self, event_id):
        return self.registrations.filter_by(event_id=event_id).first() is not None

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    registrations = db.relationship('Registration', back_populates='event', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.name}>'

    def registered_users(self):
        return [reg.user for reg in self.registrations]

class Registration(db.Model):
    __tablename__ = 'registration'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='registrations')
    event = db.relationship('Event', back_populates='registrations')

    def __repr__(self):
        return f'<Registration User:{self.user_id} Event:{self.event_id}>'