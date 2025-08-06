# app/routes.py
# Main blueprint: listing, searching, and CRUD for vehicles

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Vehicle
from . import db
from flask_login import login_required, current_user
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # … your existing search/list code with 'q' …
    return render_template('vehicles.html', vehicles=vehicles, q=q)

@main.route('/add', methods=['GET', 'POST'])
@login_required  # only logged-in users
def add_vehicle():
    """
    Only 'admin' and 'technician' can add.
    """
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied: insufficient permissions.', 'warning')
        return redirect(url_for('main.home'))

    # … your existing add logic …

@main.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """
    Only 'admin' and 'technician' can edit.
    """
    if current_user.role not in ('admin', 'technician'):
        flash('Access denied: insufficient permissions.', 'warning')
        return redirect(url_for('main.home'))

    # … your existing edit logic …

@main.route('/delete/<int:vehicle_id>')
@login_required
def delete_vehicle(vehicle_id):
    """
    Only 'admin' can delete.
    """
    if current_user.role != 'admin':
        flash('Access denied: only admins may delete.', 'warning')
        return redirect(url_for('main.home'))

    # … your existing delete logic …
