# app/routes.py

import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from sqlalchemy import or_, cast
from sqlalchemy.types import Integer

from .models import Vehicle, WorkOrder, FuelLog  # FuelLog imported so we can query fuel log entries
from . import db

# ────────────────────────────────────────────────────────────────────────────────
# Blueprint: all routes will be registered under 'main'
main = Blueprint('main', __name__)

# Allowed file extensions for uploads (images + PDFs)
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    """
    Return True if the filename’s extension is in our allowed list.
    """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT
    )

# ────────────────────────────────────────────────────────────────────────────────
@main.route('/')
@login_required
def home():
    """
    Home page:
      - GET parameters:
          q    = optional search term (make, model, or unit number)
          page = page number for pagination
      - Renders 'vehicles.html' with:
          vehicles         = list of Vehicle objects for the current page
          pagination       = Pagination helper (for prev/next links)
          q                = the original search term (so the form can re-populate)
          current_vehicle  = the first vehicle on this page (for the detail pane)
          fuel_logs        = list of FuelLog entries for current_vehicle
    """
    # 1) Read query params
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    # 2) Build base query and apply search filter if needed
    query = Vehicle.query
    if q:
        query = query.filter(
            or_(
                Vehicle.make.ilike(f'%{q}%'),
                Vehicle.model.ilike(f'%{q}%'),
                Vehicle.unit_no.ilike(f'%{q}%')
            )
        )

    # 3) Order by unit_no numerically, then paginate
    pagination = query.order_by(
        cast(Vehicle.unit_no, Integer)
    ).paginate(page=page, per_page=10, error_out=False)

    # Extract the items for this page
    vehicles = pagination.items

    # 4) Pick the first vehicle as the “current” one (or None if list is empty)
    current_vehicle = vehicles[0] if vehicles else None

    # 5) Load its fuel-log entries via the Vehicle.fuel_logs relationship
    fuel_logs = current_vehicle.fuel_logs.all() if current_vehicle else []

    # 6) Render the template with all the data
    return render_template(
        'vehicles.html',
        vehicles=vehicles,
        pagination=pagination,
        q=q,
        current_vehicle=current_vehicle,
        fuel_logs=fuel_logs
    )

# ────────────────────────────────────────────────────────────────────────────────
@main.route('/vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def vehicle_detail(vehicle_id):
    """
    Vehicle detail page:
      - GET: show vehicle info, current mileage form, list of work orders
      - POST: either update mileage, or add a new work order with optional attachment
    """
    v = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        # ----- Mileage update ----- #
        if 'miles' in request.form:
            v.miles = int(request.form['miles'])
            db.session.commit()
            flash('Mileage updated.', 'success')

        # ----- New work order ----- #
        elif 'description' in request.form:
            desc = request.form['description']
            attach = request.files.get('attachment')
            attach_fn = None

            if attach and allowed_file(attach.filename):
                safe = secure_filename(attach.filename)
                attach_fn = f"{v.vin}_wo_{safe}"
                attach.save(
                    os.path.join(current_app.config['UPLOAD_FOLDER'], attach_fn)
                )

            wo = WorkOrder(
                vehicle_id=vehicle_id,
                description=desc,
                attachment_filename=attach_fn
            )
            db.session.add(wo)
            db.session.commit()
            flash('Work order added.', 'success')

        return redirect(url_for('main.vehicle_detail', vehicle_id=vehicle_id))

    # GET → render the detail page
    return render_template('vehicle_detail.html', vehicle=v)

# ────────────────────────────────────────────────────────────────────────────────
@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    """
    Add a new vehicle:
      - Access: admin or technician only
      - Form fields: unit_no, make, model, year, vin
      - Optional file uploads: photo, invoice
    """
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied.', 'warning')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # 1) Collect form data
        unit_no = request.form['unit_no']
        make    = request.form['make']
        model   = request.form['model']
        year    = int(request.form['year'])
        vin     = request.form['vin']

        # 2) Handle photo upload
        photo = request.files.get('photo')
        photo_fn = None
        if photo and allowed_file(photo.filename):
            safe = secure_filename(photo.filename)
            photo_fn = f"{vin}_{safe}"
            photo.save(
                os.path.join(current_app.config['UPLOAD_FOLDER'], photo_fn)
            )

        # 3) Handle invoice upload
        invoice = request.files.get('invoice')
        invoice_fn = None
        if invoice and allowed_file(invoice.filename):
            safe = secure_filename(invoice.filename)
            invoice_fn = f"{vin}_invoice_{safe}"
            invoice.save(
                os.path.join(current_app.config['UPLOAD_FOLDER'], invoice_fn)
            )

        # 4) Create vehicle record & commit
        v = Vehicle(
            unit_no=unit_no,
            make=make,
            model=model,
            year=year,
            vin=vin,
            photo_filename=photo_fn,
            invoice_filename=invoice_fn
        )
        db.session.add(v)
        db.session.commit()
        flash('Vehicle added.', 'success')
        return redirect(url_for('main.home'))

    # GET → show the add-vehicle form
    return render_template('add_vehicle.html')

# ────────────────────────────────────────────────────────────────────────────────
@main.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """
    Edit an existing vehicle:
      - Access: admin or technician only
      - Fields: unit_no, make, model, year, vin
      - Optional file replacements: photo, invoice
    """
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied.', 'warning')
        return redirect(url_for('main.home'))

    v = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        # Update basic fields
        v.unit_no = request.form['unit_no']
        v.make    = request.form['make']
        v.model   = request.form['model']
        v.year    = int(request.form['year'])
        v.vin     = request.form['vin']

        # Replace photo if uploaded
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            safe = secure_filename(photo.filename)
            fn = f"{v.vin}_{safe}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
            v.photo_filename = fn

        # Replace invoice if uploaded
        invoice = request.files.get('invoice')
        if invoice and allowed_file(invoice.filename):
            safe = secure_filename(invoice.filename)
            fn = f"{v.vin}_invoice_{safe}"
            invoice.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
            v.invoice_filename = fn

        db.session.commit()
        flash('Vehicle updated.', 'success')
        return redirect(url_for('main.home'))

    # GET → show the edit form
    return render_template('edit_vehicle.html', vehicle=v)

# ────────────────────────────────────────────────────────────────────────────────
@main.route('/delete/<int:vehicle_id>')
@login_required
def delete_vehicle(vehicle_id):
    """
    Delete a vehicle:
      - Access: admin only
      - Cascades to remove related work orders via model backref
    """
    if current_user.role != 'admin':
        flash('Access denied.', 'warning')
        return redirect(url_for('main.home'))

    v = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(v)
    db.session.commit()
    flash('Vehicle deleted.', 'success')
    return redirect(url_for('main.home'))
