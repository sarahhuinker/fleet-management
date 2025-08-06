# app/models.py

# This file will eventually hold our database models.
# For now, we will simulate data manually.

class Vehicle:
    def __init__(self, id, make, model, year, vin):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.vin = vin
# models.py will store data models like vehicles, technicians, etc.
