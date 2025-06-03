from flask import render_template, redirect, url_for, flash, session, request
from app import app, db
from app.models import User, Event, Registration
from app.forms import LoginForm, AddUserForm, EventForm, EditEventForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/users', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('users'))

from app.forms import EditUserForm

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
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
@login_required
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
@login_required
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
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('events'))

@app.route('/dashboard')
@login_required
def dashboard():
    events = Event.query.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())
    user_registrations = [reg.event for reg in current_user.registrations]
    return render_template('dashboard.html', user=current_user, events=events, user_registrations=user_registrations)

@app.route('/register_event/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    if not current_user.is_authenticated:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))
    if not Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first():
        reg = Registration(user_id=current_user.id, event_id=event_id)
        db.session.add(reg)
        db.session.commit()
        flash('Registered for event!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/unregister_event/<int:event_id>', methods=['POST'])
@login_required
def unregister_event(event_id):
    if not current_user.is_authenticated:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))
    reg = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Unregistered from event.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/registrations')
@login_required
def registrations():
    events = Event.query.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())
    return render_template('registrations.html', events=events)

@app.route('/schema')
@login_required
def schema():
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

@app.route('/search_events', methods=['GET'])
@login_required
def search_events():
    search_query = request.args.get('search', '')
    date_range = request.args.get('date', '')
    category = request.args.get('categories', '')

    filtered_events = Event.query

    if search_query:
        filtered_events = filtered_events.filter(Event.name.ilike(f'%{search_query}%'))
    if date_range:
        filtered_events = filtered_events.filter(Event.date == date_range)
    if category and hasattr(Event, 'category'):
        filtered_events = filtered_events.filter(Event.category == category)

    events = filtered_events.all()
    for event in events:
        event.attendee_count = len(event.registrations.all())

    user_registrations = [reg.event for reg in current_user.registrations]
    return render_template('dashboard.html', user=current_user, events=events, user_registrations=user_registrations)