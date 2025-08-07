# app/models.py
# Define your database models: Vehicle (with static fields + JSON blob + uploads), WorkOrder, FuelLog, and User

import datetime
from datetime import date
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Vehicle(db.Model):
    """
    Vehicle model:
      - id:                Primary key
      - unit_no:           Vehicle unit number for internal identification and sorting
      - make, model, year: Static columns for easy forms & queries
      - vin:               Unique identifier
      - photo_filename:    Optional image upload filename
      - invoice_filename:  Optional invoice (PDF/image) upload filename
      - data:              JSON blob storing all extra CSV‐based fields
    """
    __tablename__       = 'vehicle'

    # ─ Primary Key ─────────────────────────────────────────────────────────────
    id                   = db.Column(db.Integer, primary_key=True)

    # ─ Static columns ─────────────────────────────────────────────────────────
    unit_no              = db.Column(db.String(50), nullable=True)   # Unit number for sorting and quick reference
    make                 = db.Column(db.String(80), nullable=True)   # Manufacturer name
    model                = db.Column(db.String(80), nullable=True)   # Model name
    year                 = db.Column(db.Integer, nullable=True)      # Model year

    # ─ Unique & Uploads ───────────────────────────────────────────────────────
    vin                  = db.Column(db.String(120), unique=True, nullable=False)  # Vehicle Identification Number
    photo_filename       = db.Column(db.String(255), nullable=True)  # Filename for uploaded vehicle photo
    invoice_filename     = db.Column(db.String(255), nullable=True)  # Filename for uploaded invoice PDF or image

    # ─ JSON blob for dynamic fields ────────────────────────────────────────────
    data                 = db.Column(JSON, nullable=False, default=dict)  # Store any additional CSV/imported data here

    # ─ Relationship to FuelLog ──────────────────────────────────────────────────
    # one-to-many link to FuelLog, sorted by date descending
    fuel_logs            = db.relationship(
                             'FuelLog',
                             backref='vehicle',
                             lazy='dynamic',
                             order_by="FuelLog.date.desc()"
                         )

    def __repr__(self):
        return f'<Vehicle {self.unit_no or self.id}: {self.make} {self.model}>'

class WorkOrder(db.Model):
    """
    WorkOrder model:
      - id:                     Primary key
      - vehicle_id:             FK → vehicle.id
      - description:            Text description of the work order task
      - date:                   Date the work order was created (defaults to today)
      - attachment_filename:    Optional file upload (PDF/image) related to the work order
    """
    __tablename__         = 'work_order'
    id                    = db.Column(db.Integer, primary_key=True)   # WorkOrder primary key
    vehicle_id            = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)  # Associated vehicle
    description           = db.Column(db.Text, nullable=False)        # Details of the work to be performed
    date                  = db.Column(db.Date, nullable=False, default=datetime.date.today)  # Date of creation
    attachment_filename   = db.Column(db.String(255), nullable=True)  # Filename for any uploaded attachment

    # Relationship back to Vehicle with cascade delete
    vehicle               = db.relationship(
        'Vehicle',
        backref=db.backref('work_orders', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f'<WorkOrder {self.id} for Vehicle {self.vehicle_id}>'

class FuelLog(db.Model):
    """
    FuelLog model:
      - id:                Primary key
      - vehicle_id:        FK → vehicle.id
      - date:              Date of fueling
      - last_od:           Odometer reading at last fill
      - curr_od:           Odometer reading at current fill
      - gallons:           Gallons purchased
      - total_cost:        Total cost of the fill-up
      - cost_per_gallon:   Calculated property
      - mpg:               Calculated miles per gallon property
    """
    __tablename__ = 'fuel_log'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)  # Fueling date
    last_od = db.Column(db.Integer, nullable=False)               # Previous odometer
    curr_od = db.Column(db.Integer, nullable=False)               # Current odometer
    gallons = db.Column(db.Float, nullable=False)                 # Gallons purchased
    total_cost = db.Column(db.Float, nullable=False)              # Total dollars spent

    @property
    def cost_per_gallon(self):
        """Dollars per gallon."""
        return self.total_cost / self.gallons if self.gallons else 0

    @property
    def mpg(self):
        """Miles per gallon."""
        miles = self.curr_od - self.last_od
        return miles / self.gallons if self.gallons else 0

class User(UserMixin, db.Model):
    """
    User model for authentication:
      - id:           Primary key
      - username:     Unique login name
      - password_hash:Hashed password for security
      - role:         User role (e.g., 'admin', 'technician', 'read-only') for authorization
    """
    __tablename__      = 'user'
    id                  = db.Column(db.Integer, primary_key=True)  # User primary key
    username            = db.Column(db.String(80), unique=True, nullable=False)  # Login name
    password_hash       = db.Column(db.String(128), nullable=False)  # Hashed password
    role                = db.Column(db.String(20), nullable=False, default='read-only')  # Authorization role

    def set_password(self, pw):
        """Hash & store the user’s password."""
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        """Check a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, pw)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
