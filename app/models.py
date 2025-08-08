from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

# ────────────────────────────────────────────────────────────────────────────────
class Vehicle(db.Model):
    """
    Vehicle model:
    - Fleetmate-style fields for core identity, tracking, and renewals
    - Upload fields for image and invoice
    - JSON blob for import flexibility
    """
    __tablename__ = 'vehicle'

    id                 = db.Column(db.Integer, primary_key=True)
    unit_no            = db.Column(db.String(50), nullable=True)
    make               = db.Column(db.String(80), nullable=True)
    model              = db.Column(db.String(80), nullable=True)
    year               = db.Column(db.Integer, nullable=True)
    vin                = db.Column(db.String(120), unique=True, nullable=False)

    # Uploads
    photo_filename     = db.Column(db.String(255), nullable=True)
    invoice_filename   = db.Column(db.String(255), nullable=True)

    # Classification
    body               = db.Column(db.String(50), nullable=True)
    type               = db.Column(db.String(50), nullable=True)

    # Tracking
    odometer           = db.Column(db.Integer, nullable=True)
    hours              = db.Column(db.Integer, nullable=True)

    # Renewals
    registration_exp   = db.Column(db.Date, nullable=True)
    inspection_exp     = db.Column(db.Date, nullable=True)
    insurance_exp      = db.Column(db.Date, nullable=True)

    # Organization
    chargeback         = db.Column(db.String(100), nullable=True)
    department         = db.Column(db.String(100), nullable=True)
    manager            = db.Column(db.String(50), nullable=True)
    director           = db.Column(db.String(50), nullable=True)

    # Location
    location           = db.Column(db.String(100), nullable=True)
    building           = db.Column(db.String(100), nullable=True)

    # Extra JSON blob
    data               = db.Column(JSON, nullable=False, default=dict)

    # Relationships
    fuel_logs = db.relationship(
        'FuelLog',
        backref='vehicle',
        lazy='dynamic',
        order_by="FuelLog.date.desc()"
    )

    work_orders = db.relationship(
        'WorkOrder',
        backref='vehicle',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    maintenance_logs = db.relationship(
        'MaintenanceLog',
        backref='vehicle',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Vehicle {self.unit_no or self.id}: {self.make} {self.model}>'

# ────────────────────────────────────────────────────────────────────────────────
class WorkOrder(db.Model):
    """
    WorkOrder model:
    - Linked to vehicle
    - Supports text description and optional file
    """
    __tablename__ = 'work_order'

    id                  = db.Column(db.Integer, primary_key=True)
    vehicle_id          = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    description         = db.Column(db.Text, nullable=False)
    date                = db.Column(db.Date, nullable=False, default=date.today)
    attachment_filename = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<WorkOrder {self.id} for Vehicle {self.vehicle_id}>'

# ────────────────────────────────────────────────────────────────────────────────
class FuelLog(db.Model):
    """
    FuelLog model:
    - Tracks odometer, gallons, cost, and calculates MPG & $/gallon
    """
    __tablename__ = 'fuel_log'

    id           = db.Column(db.Integer, primary_key=True)
    vehicle_id   = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    date         = db.Column(db.Date, nullable=False, default=date.today)
    last_od      = db.Column(db.Integer, nullable=False)
    curr_od      = db.Column(db.Integer, nullable=False)
    gallons      = db.Column(db.Float, nullable=False)
    total_cost   = db.Column(db.Float, nullable=False)

    @property
    def cost_per_gallon(self):
        return self.total_cost / self.gallons if self.gallons else 0

    @property
    def mpg(self):
        miles = self.curr_od - self.last_od
        return miles / self.gallons if self.gallons else 0

    def __repr__(self):
        return f'<FuelLog {self.date} for Vehicle {self.vehicle_id}>'

# ────────────────────────────────────────────────────────────────────────────────
class MaintenanceLog(db.Model):
    """
    MaintenanceLog model:
    - Linked to a vehicle
    - Tracks date, service type, notes, and cost
    """
    __tablename__ = 'maintenance_log'

    id           = db.Column(db.Integer, primary_key=True)
    vehicle_id   = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    service_type = db.Column(db.String(100), nullable=False)
    notes        = db.Column(db.Text)
    cost         = db.Column(db.Float)

    def __repr__(self):
        return f'<MaintenanceLog {self.service_date} for Vehicle {self.vehicle_id}>'

# ────────────────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    """
    User model for login and roles
    - Supports hashed passwords
    - Can be admin, technician, or read-only
    """
    __tablename__ = 'user'

    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80), unique=True, nullable=False)
    password_hash  = db.Column(db.String(128), nullable=False)
    role           = db.Column(db.String(20), nullable=False, default='read-only')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
