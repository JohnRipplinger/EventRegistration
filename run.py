from app import app, db
from app.models import User, Event, Registration

def seed_db():
    # Only seed if there are no users/events
    if User.query.first() or Event.query.first():
        return  # Already seeded

    from datetime import date
    users = [
        User(username='admin', email='admin@example.com'),
        User(username='alice', email='alice@example.com'),
        User(username='bob', email='bob@example.com'),
        User(username='carol', email='carol@example.com'),
    ]
    db.session.add_all(users)
    db.session.commit()

    events = [
        Event(name='Flask Workshop', date=date(2025, 6, 1), location='Room 101'),
        Event(name='Python Meetup', date=date(2025, 6, 15), location='Room 202'),
        Event(name='Tech Conference', date=date(2025, 7, 10), location='Main Hall'),
    ]
    db.session.add_all(events)
    db.session.commit()

    registrations = [
        Registration(user_id=users[0].id, event_id=events[0].id),
        Registration(user_id=users[1].id, event_id=events[0].id),
        Registration(user_id=users[1].id, event_id=events[1].id),
        Registration(user_id=users[2].id, event_id=events[2].id),
    ]
    db.session.add_all(registrations)
    db.session.commit()
    print("Database seeded!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(debug=True)