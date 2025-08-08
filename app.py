# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Import and register blueprints
from app.routes import main
from app.auth import auth  # Optional: if you have auth routes

app.register_blueprint(main)
app.register_blueprint(auth)  # Only include this if your app has authentication

# User loader for Flask-Login
from app.models import User  # Replace with your user model if different

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
