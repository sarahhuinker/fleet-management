# app/routes.py

from flask import Blueprint, render_template
from .models import Vehicle

main = Blueprint('main', __name__)

# Dummy vehicle data
vehicles = [
    Vehicle(1, "Ford", "F-150", 2022, "1FTFW1E50NFA00001"),
    Vehicle(2, "Chevy", "Silverado", 2021, "3GCNWAEF4MG100002"),
    Vehicle(3, "Dodge", "Durango", 2020, "1C4RDJDG0LC300003")
]

@main.route('/')
def home():
    return "Hello, Sarah! Your Flask app is running 💥"

@main.route('/vehicles')
def vehicle_list():
    return render_template('vehicles.html', vehicles=vehicles)


