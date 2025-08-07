# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ── Initialize extensions ───────────────────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()

# ── Import models so SQLAlchemy sees them before create_all() ───────────────────
from .models import Vehicle, WorkOrder, User

def create_app():
    """
    Application factory:
      - Configures Flask, SQLAlchemy, and Flask-Login
      - Loads CSV headers into app.config['VEHICLE_FIELDS']
      - Sets up upload folder
      - Creates database tables
      - Registers blueprints
    """
    app = Flask(__name__)

    # ── SECRET_KEY ───────────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # ── Database config ──────────────────────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Upload config ────────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    # ── Load CSV headers for dynamic form fields ─────────────────────────────────
    # app.root_path ends at .../my-webapp/app, so os.pardir brings us to project root
    project_root = os.path.abspath(os.path.join(app.root_path, os.pardir))
    header_path = os.path.join(project_root, 'vEHICLES.txt')
    with open(header_path, newline='') as f:
        headers = f.readline().strip().split(',')
    app.config['VEHICLE_FIELDS'] = headers

    # ── Initialize extensions with app ────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # ── Create database tables (if they don’t exist) ─────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Register blueprints ───────────────────────────────────────────────────────
    from .routes import main
    from .auth   import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
