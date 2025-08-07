# app/models.py
# Define Vehicle (with all new fields) and WorkOrder for attachments.

import datetime
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Vehicle(db.Model):
    """
    Extended Vehicle model with all fields from the detail UI.
    """
    __tablename__      = 'vehicle'
    id                  = db.Column(db.Integer, primary_key=True)
    # Basic info
    vin                 = db.Column(db.String(120), unique=True, nullable=False)
    make                = db.Column(db.String(80), nullable=False)
    model               = db.Column(db.String(80), nullable=False)
    year                = db.Column(db.Integer, nullable=False)
    energy              = db.Column(db.String(20), nullable=True)   # e.g. IC, Electric
    category            = db.Column(db.String(50), nullable=True)   # e.g. Motor Vehicle
    type                = db.Column(db.String(50), nullable=True)   # e.g. SUV
    body                = db.Column(db.String(50), nullable=True)   # e.g. SUV
    ownership           = db.Column(db.String(50), nullable=True)   # e.g. Owned
    customer            = db.Column(db.String(100), nullable=True)

    # Asset Identifiers
    veh_no              = db.Column(db.String(50), nullable=True)
    unit_no             = db.Column(db.String(50), nullable=True)
    tag_no              = db.Column(db.String(50), nullable=True)
    entity_code         = db.Column(db.String(50), nullable=True)

    # Tracking & Utilization
    odometer            = db.Column(db.Integer, nullable=False, default=0)
    hours               = db.Column(db.Integer, nullable=False, default=0)
    utilization_mode    = db.Column(db.String(10), nullable=False, default='odometer')
    auto_utilization    = db.Column(db.Boolean, nullable=False, default=False)

    # Renewals
    registration_date   = db.Column(db.Date, nullable=True)
    emission_date       = db.Column(db.Date, nullable=True)
    inspection_date     = db.Column(db.Date, nullable=True)
    insurance_date      = db.Column(db.Date, nullable=True)

    # Operator Location & Notification
    operator            = db.Column(db.String(50), nullable=True)
    location            = db.Column(db.String(100), nullable=True)
    building            = db.Column(db.String(100), nullable=True)
    email               = db.Column(db.String(120), nullable=True)
    sms                 = db.Column(db.String(50), nullable=True)
    ezpass              = db.Column(db.String(50), nullable=True)
    fuel_card           = db.Column(db.String(50), nullable=True)

    # Organization
    chargeback          = db.Column(db.String(100), nullable=True)
    department          = db.Column(db.String(100), nullable=True)
    manager             = db.Column(db.String(50), nullable=True)
    director            = db.Column(db.String(50), nullable=True)

    # Work Order Defaults
    default_wodefault   = db.Column(db.String(20), nullable=True)  # "Employee" or "Vendor"
    default_vendor      = db.Column(db.String(50), nullable=True)
    default_issued_by   = db.Column(db.String(50), nullable=True)
    default_parts_vendor= db.Column(db.String(50), nullable=True)
    inventory_warehouse = db.Column(db.String(50), nullable=True)

    # Custom Fields (you could store JSON here or a long text)
    custom_fields       = db.Column(db.Text, nullable=True)

    # Mileage
    miles               = db.Column(db.Integer, nullable=False, default=0)

    # Optional uploads
    photo_filename      = db.Column(db.String(255), nullable=True)
    invoice_filename    = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Vehicle {self.id}: {self.make} {self.model}>'


class WorkOrder(db.Model):
    """
    WorkOrder model for attachments on detail page.
    """
    __tablename__         = 'work_order'
    id                    = db.Column(db.Integer, primary_key=True)
    vehicle_id            = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    description           = db.Column(db.Text, nullable=False)
    date                  = db.Column(db.Date, nullable=False, default=datetime.date.today)
    attachment_filename   = db.Column(db.String(255), nullable=True)

    # Back-reference to Vehicle
    vehicle               = db.relationship(
        'Vehicle',
        backref=db.backref('work_orders', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f'<WorkOrder {self.id} for Vehicle {self.vehicle_id}>'


class User(UserMixin, db.Model):
    """
    Unchanged User model for authentication.
    """
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
