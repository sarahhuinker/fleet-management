from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Vehicle(db.Model):
    __tablename__      = 'vehicle'
    id                  = db.Column(db.Integer, primary_key=True)
    make                = db.Column(db.String(80), nullable=False)
    model               = db.Column(db.String(80), nullable=False)
    year                = db.Column(db.Integer, nullable=False)
    vin                 = db.Column(db.String(120), unique=True, nullable=False)
    photo_filename      = db.Column(db.String(255), nullable=True)  # stores image name
    invoice_filename    = db.Column(db.String(255), nullable=True)  # stores PDF/image invoice

    def __repr__(self):
        return f'<Vehicle {self.id}: {self.make} {self.model}>'

class User(UserMixin, db.Model):
    __tablename__      = 'user'
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(80), unique=True, nullable=False)
    password_hash       = db.Column(db.String(128), nullable=False)
    role                = db.Column(db.String(20), nullable=False, default='read-only')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
