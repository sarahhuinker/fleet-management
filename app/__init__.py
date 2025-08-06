# Initializes the Flask application and registers the blueprint

from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register the routes (now located directly in app/routes.py)
    from .routes import main
    app.register_blueprint(main)

    return app
