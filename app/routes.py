# app/routes.py
# Main blueprint: listing (with search & pagination), plus CRUD routes

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Vehicle
from . import db
from flask_login import login_required, current_user
from sqlalchemy import or_  # to OR the search filters

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """
    Home page:
    - Supports optional 'q' query parameter for searching by make or model
    - Supports optional 'page' query parameter for pagination
    """
    # 1. Read query params: search term 'q' and page number 'page'
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    # 2. Build base SQLAlchemy query
    query = Vehicle.query
    if q:
        # 2a. Apply case-insensitive search filter on make OR model
        query = query.filter(
            or_(
                Vehicle.make.ilike(f'%{q}%'),
                Vehicle.model.ilike(f'%{q}%')
            )
        )

    # 3. Paginate: returns a Pagination object
    pagination = query.order_by(Vehicle.id).paginate(
        page=page,        # which page to return
        per_page=10,      # items per page
        error_out=False   # don’t 404 if page is out of range
    )

    vehicles = pagination.items  # the list of Vehicle objects for this page

    # 4. Render template with:
    #    - vehicles: current page’s items
    #    - pagination: Pagination object for prev/next, page numbers
    #    - q: original search term to preserve in links/forms
    return render_template(
        'vehicles.html',
        vehicles=vehicles,
        pagination=pagination,
        q=q
    )

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    # … your existing add_vehicle code …
    pass

@main.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    # … your existing edit_vehicle code …
    pass

@main.route('/delete/<int:vehicle_id>')
@login_required
def delete_vehicle(vehicle_id):
    # … your existing delete_vehicle code …
    pass


