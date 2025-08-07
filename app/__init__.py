import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# import models so SQLAlchemy sees them before create_all()
from .models import Vehicle, User

def create_app():
    app = Flask(__name__)

    # SECRET_KEY for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── UPLOAD CONFIG ────────────────────────────────────────────────
    # Files will go into app/static/uploads
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # Limit uploads to 16 MB
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Create tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes import main
    from .auth   import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
