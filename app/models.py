# app/models.py
# Database models: Vehicle and User for authentication

from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Vehicle(db.Model):
    """
    Vehicle model:
    - __tablename__: explicit table name
    - id:   Primary key
    - make: Vehicle manufacturer (e.g., Ford)
    - model: Vehicle model (e.g., F-150)
    - year: Production year (e.g., 2022)
    - vin:  Vehicle Identification Number (unique)
    """
    __tablename__ = 'vehicle'

    id    = db.Column(db.Integer, primary_key=True)       # ← primary key!
    make  = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year  = db.Column(db.Integer, nullable=False)
    vin   = db.Column(db.String(120), nullable=False, unique=True)

    def __repr__(self):
        return f'<Vehicle {self.id}: {self.make} {self.model}>'


class User(UserMixin, db.Model):
    """
    User model for authentication & role-based access:
    - __tablename__: explicit table name
    - id:       Primary key
    - username: unique login name
    - password_hash: hashed password
    - role:     'admin', 'technician', or 'read-only'
    """
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)       # ← primary key!
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default='read-only')

    def set_password(self, password):
        """Hash & store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
