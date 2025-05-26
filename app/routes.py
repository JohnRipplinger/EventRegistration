from flask import render_template, redirect, url_for, flash, session, request, g
from app import app, db
from app.models import User, Event, Registration
from app.forms import LoginForm, AddUserForm, EventForm, EditEventForm


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        
@app.context_processor
def inject_user():
    return dict(current_user=g.user)
        
@app.route('/')
def home():
    #return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))  # Change to user dashboard
        else:
            flash('Username not found.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/users', methods=['GET', 'POST'])
def users():
    users = User.query.all()
    add_user_form = AddUserForm()
    if add_user_form.validate_on_submit():
        username = add_user_form.username.data
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            user = User(username=username, email=add_user_form.email.data or f"{username}@example.com", is_admin=add_user_form.is_admin.data)
            db.session.add(user)
            db.session.commit()
            flash('User added!', 'success')
        return redirect(url_for('users'))
    return render_template('users.html', users=users, add_user_form=add_user_form)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('users'))

from app.forms import EditUserForm

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        # Check for unique username/email if needed
        existing_user = User.query.filter(User.username == form.username.data, User.id != user.id).first()
        existing_email = User.query.filter(User.email == form.email.data, User.id != user.id).first()
        if existing_user:
            flash('Username already exists.', 'danger')
        elif existing_email:
            flash('Email already exists.', 'danger')
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            if form.is_admin.data and not user.is_admin:
                flash('User promoted to admin.', 'success')
            db.session.commit()
            flash('User updated!', 'success')
            return redirect(url_for('users'))
    return render_template('edit_user.html', form=form, user=user)

@app.route('/events', methods=['GET', 'POST'])
def events():
    events = Event.query.all()
    event_form = EventForm()
    if event_form.validate_on_submit():
        event = Event(
            name=event_form.name.data,
            date=event_form.date.data,
            location=event_form.location.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added!', 'success')
        return redirect(url_for('events'))
    return render_template('events.html', events=events, event_form=event_form)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EditEventForm(obj=event)
    if form.validate_on_submit():
        event.name = form.name.data
        event.date = form.date.data
        event.location = form.location.data
        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('events'))
    return render_template('edit_event.html', form=form, event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('events'))

from app.models import Registration, Event

@app.route('/dashboard')
def dashboard():
    if not g.user:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    events = Event.query.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())  # Convert to list
    #user_registrations = {reg.event_id for reg in g.user.registrations}
    user_registrations = {reg.event for reg in g.user.registrations}
    return render_template('dashboard.html', user=g.user, events=events, user_registrations=user_registrations)

@app.route('/register_event/<int:event_id>', methods=['POST'])
def register_event(event_id):
    if not g.user:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))
    if not Registration.query.filter_by(user_id=g.user.id, event_id=event_id).first():
        reg = Registration(user_id=g.user.id, event_id=event_id)
        db.session.add(reg)
        db.session.commit()
        flash('Registered for event!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/unregister_event/<int:event_id>', methods=['POST'])
def unregister_event(event_id):
    if not g.user:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))
    reg = Registration.query.filter_by(user_id=g.user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Unregistered from event.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/registrations')
def registrations():
    events = Event.query.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())  # Convert to list

    return render_template('registrations.html', events=events)

@app.route('/schema')
def schema():
    # Import models here to ensure latest definitions are used
    from app.models import User, Event, Registration

    models = [User, Event, Registration]
    schema_info = []

    for model in models:
        columns = []
        for col in model.__table__.columns:
            columns.append({
                'name': col.name,
                'type': str(col.type),
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'unique': col.unique,
            })
        # Gather relationships for this model
        rels = []
        for rel in model.__mapper__.relationships:
            rels.append({
                'name': rel.key,
                'target': rel.mapper.class_.__name__,
                'direction': str(rel.direction)
            })
        schema_info.append({
            'model': model.__name__,
            'columns': columns,
            'relationships': rels
        })
    return render_template('schema.html', schema_info=schema_info)

from flask import request, render_template
from app import app, db
from app.models import Event

@app.route('/search_events', methods=['GET'])
def search_events():
    search_query = request.args.get('search', '')
    date_range = request.args.get('date', '')
    category = request.args.get('categories', '')

    # Start with all events
    filtered_events = Event.query

    # Apply search filter
    if search_query:
        filtered_events = filtered_events.filter(Event.name.ilike(f'%{search_query}%'))

    # Apply date filter
    if date_range:
        filtered_events = filtered_events.filter(Event.date == date_range)

    # Apply category filter
    if category:
        filtered_events = filtered_events.filter(Event.category == category)

    events = filtered_events.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())

    return render_template('dashboard.html', user=g.user, events=events)