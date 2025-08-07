# app/models.py
# Define your database models: Vehicle (with static fields + JSON blob + uploads), WorkOrder, and User

import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Vehicle(db.Model):
    """
    Vehicle model:
      - id:                Primary key
      - make, model, year: Static columns for easy forms & queries
      - vin:               Unique identifier
      - photo_filename:    Optional image upload filename
      - invoice_filename:  Optional invoice (PDF/image) upload filename
      - data:              JSON blob storing all extra CSV‐based fields
    """
    __tablename__       = 'vehicle'
    id                   = db.Column(db.Integer, primary_key=True)

    # ─ Static columns ─────────────────────────────────────────────────────────
    make                 = db.Column(db.String(80), nullable=True)
    model                = db.Column(db.String(80), nullable=True)
    year                 = db.Column(db.Integer, nullable=True)

    vin                  = db.Column(db.String(120), unique=True, nullable=False)
    photo_filename       = db.Column(db.String(255), nullable=True)
    invoice_filename     = db.Column(db.String(255), nullable=True)

    # JSON to hold all other dynamic CSV fields, if you still want them
    data                 = db.Column(JSON, nullable=False, default={})

    def __repr__(self):
        return f'<Vehicle {self.id}: {self.make} {self.model}>'

class WorkOrder(db.Model):
    """
    WorkOrder model:
      - id:                     Primary key
      - vehicle_id:             FK → vehicle.id
      - description:            Text of the work order
      - date:                   Date created (defaults to today)
      - attachment_filename:    Optional file upload (PDF/image)
    """
    __tablename__         = 'work_order'
    id                    = db.Column(db.Integer, primary_key=True)
    vehicle_id            = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    description           = db.Column(db.Text, nullable=False)
    date                  = db.Column(db.Date, nullable=False, default=datetime.date.today)
    attachment_filename   = db.Column(db.String(255), nullable=True)

    # Relationship back to Vehicle
    vehicle               = db.relationship(
        'Vehicle',
        backref=db.backref('work_orders', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f'<WorkOrder {self.id} for Vehicle {self.vehicle_id}>'

class User(UserMixin, db.Model):
    """
    User model for authentication:
      - id:           PK
      - username:     Unique
      - password_hash
      - role:         e.g. 'admin', 'technician', 'read-only'
    """
    __tablename__      = 'user'
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(80), unique=True, nullable=False)
    password_hash       = db.Column(db.String(128), nullable=False)
    role                = db.Column(db.String(20), nullable=False, default='read-only')

    def set_password(self, pw):
        """Hash & store the user’s password."""
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        """Check a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, pw)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
