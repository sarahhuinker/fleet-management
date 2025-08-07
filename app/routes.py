# app/routes.py
# Main blueprint: list, detail (+mileage & work orders), add/edit/delete vehicles (with uploads)

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
from sqlalchemy import or_

from .models import Vehicle, WorkOrder
from . import db

main = Blueprint('main', __name__)

# ── Allowed file extensions for uploads (images + PDFs) ─────────────────────────
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    """
    Return True if the filename has an allowed extension.
    """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT
    )

@main.route('/')
def home():
    """
    Home page:
      - Optional search by make/model via ?q=term
      - Optional pagination via ?page=N
    """
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    # 1) Base query
    query = Vehicle.query
    if q:
        # Filter on make OR model (case-insensitive)
        query = query.filter(
            or_(
                Vehicle.make.ilike(f'%{q}%'),
                Vehicle.model.ilike(f'%{q}%')
            )
        )

    # 2) Paginate results (10 per page)
    pagination = query.order_by(Vehicle.id).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    vehicles = pagination.items

    # 3) Render template
    return render_template(
        'vehicles.html',
        vehicles=vehicles,
        pagination=pagination,
        q=q
    )

@main.route('/vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def vehicle_detail(vehicle_id):
    """
    Vehicle detail page:
      GET: display vehicle info, mileage form, and list of work orders.
      POST: either update mileage or create a new work order (with optional attachment).
    """
    v = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        # -- Mileage update --
        if 'miles' in request.form:
            v.miles = int(request.form['miles'])
            db.session.commit()
            flash('Mileage updated.', 'success')

        # -- New work order --
        elif 'description' in request.form:
            desc = request.form['description']
            # Handle optional attachment upload
            attach = request.files.get('attachment')
            attach_fn = None
            if attach and allowed_file(attach.filename):
                safe = secure_filename(attach.filename)
                attach_fn = f"{v.vin}_wo_{safe}"
                attach.save(os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    attach_fn
                ))

            wo = WorkOrder(
                vehicle_id=vehicle_id,
                description=desc,
                attachment_filename=attach_fn
            )
            db.session.add(wo)
            db.session.commit()
            flash('Work order created.', 'success')

        return redirect(url_for('main.vehicle_detail', vehicle_id=vehicle_id))

    # GET → render detail page
    return render_template('vehicle_detail.html', vehicle=v)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    """
    Add a new vehicle:
      - Only 'admin' or 'technician' may add.
      - Supports photo + PDF/image invoice uploads.
    """
    # Permission guard
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied: insufficient permissions.', 'warning')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # -- Text fields --
        make, model = request.form['make'], request.form['model']
        year, vin   = int(request.form['year']), request.form['vin']

        # -- Photo upload --
        photo    = request.files.get('photo')
        photo_fn = None
        if photo and allowed_file(photo.filename):
            safe = secure_filename(photo.filename)
            photo_fn = f"{vin}_{safe}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], photo_fn))

        # -- Invoice upload --
        invoice    = request.files.get('invoice')
        invoice_fn = None
        if invoice and allowed_file(invoice.filename):
            safe        = secure_filename(invoice.filename)
            invoice_fn  = f"{vin}_invoice_{safe}"
            invoice.save(os.path.join(current_app.config['UPLOAD_FOLDER'], invoice_fn))

        # -- Create & commit Vehicle --
        v = Vehicle(
            make=make,
            model=model,
            year=year,
            vin=vin,
            photo_filename=photo_fn,
            invoice_filename=invoice_fn
        )
        db.session.add(v)
        db.session.commit()

        return redirect(url_for('main.home'))

    # GET → show the add form
    return render_template('add_vehicle.html')

@main.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """
    Edit an existing vehicle:
      - Only 'admin' or 'technician' may edit.
      - Allows replacing photo and invoice files.
    """
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied: insufficient permissions.', 'warning')
        return redirect(url_for('main.home'))

    v = Vehicle.query.get_or_404(vehicle_id)
    if request.method == 'POST':
        # -- Update text fields --
        v.make, v.model = request.form['make'], request.form['model']
        v.year, v.vin   = int(request.form['year']), request.form['vin']

        # -- Replace photo if uploaded --
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            safe = secure_filename(photo.filename)
            fn = f"{v.vin}_{safe}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
            v.photo_filename = fn

        # -- Replace invoice if uploaded --
        invoice = request.files.get('invoice')
        if invoice and allowed_file(invoice.filename):
            safe = secure_filename(invoice.filename)
            fn = f"{v.vin}_invoice_{safe}"
            invoice.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
            v.invoice_filename = fn

        db.session.commit()
        return redirect(url_for('main.home'))

    # GET → show edit form
    return render_template('edit_vehicle.html', vehicle=v)

@main.route('/delete/<int:vehicle_id>')
@login_required
def delete_vehicle(vehicle_id):
    """
    Delete a vehicle (admin only).
    """
    if current_user.role != 'admin':
        flash('Access denied: only admins may delete.', 'warning')
        return redirect(url_for('main.home'))

    v = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for('main.home'))
