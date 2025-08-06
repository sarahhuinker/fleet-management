from flask import Blueprint, render_template

main = Blueprint('main', __name__)

# temporary dummy data
class Vehicle:
    def __init__(self, id, make, model, year, vin):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.vin = vin

vehicles = [
    Vehicle(1, "Ford", "F-150", 2022, "1FTFW1E50NFA00001"),
    Vehicle(2, "Chevy", "Silverado", 2021, "3GCNWAEF4MG100002"),
    Vehicle(3, "Dodge", "Durango", 2020, "1C4RDJDG0LC300003"),
]

@main.route('/')
def home():
    return render_template('vehicles.html', vehicles=vehicles)



