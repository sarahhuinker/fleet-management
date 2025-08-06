# app/auth.py
# Blueprint for user registration, login, and logout

from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from . import db, login_manager
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user:
    - GET:  show registration form
    - POST: validate, create user, redirect to login
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role     = request.form['role']

        # Prevent duplicate usernames
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))

        # Create & save new user
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    """Given a user ID, return the corresponding User object."""
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in an existing user:
    - GET:  show login form
    - POST: verify credentials, call login_user, redirect to home
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect home."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
