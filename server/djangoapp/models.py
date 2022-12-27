from django.db import models
from django.utils.timezone import now
from dataclasses import dataclass


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    name = models.CharField(null=False, max_length=100)
    dealer_id = models.IntegerField(null=False)
    car_type = models.CharField(null=False, max_length=50, choices=(
        ("Sedan", "Sedan"), ("SUV", "SUV"), ("WAGON", "WAGON")))
    year = models.IntegerField(null=False)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
@dataclass
class CarDealer:
    address: str
    city: str
    full_name: str
    short_name: str
    id: int
    lat: float
    long: float
    st: str
    state: str
    zip: str

    def __str__(self) -> str:
        return f"{self.full_name}"


# <HINT> Create a plain Python class `DealerReview` to hold review data
@dataclass
class DealerReview:
    car_make: str
    car_model: str
    car_year: int
    dealership: int
    sentiment: str
    emotion: str
    emotion_color: str
    reviewer: str
    purchase: bool
    purchase_date: str
    review: str

    def __str__(self) -> str:
        return f"{self.reviewer}"
