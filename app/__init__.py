# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ── Initialize extensions ───────────────────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()

# ── Import your models so SQLAlchemy knows about them before create_all() ───────
from .models import Vehicle, User

def create_app():
    app = Flask(__name__)

    # ── SECRET_KEY ────────────────────────────────────────────────────────────────
    # Used for session signing and Flask-Login.
    # In production, set the SECRET_KEY config var. Fallback to this only for local dev.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # ── Database config ──────────────────────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Initialize extensions with app ────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # ── Create tables ─────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Register blueprints ───────────────────────────────────────────────────────
    from .routes import main
    from .auth   import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
