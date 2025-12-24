
from django.db import models

# Database Model for storing house price predictions
class HousePrice(models.Model):
    price = models.BigIntegerField()
    area = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    stories = models.IntegerField()
    mainroad = models.IntegerField()
    guestroom = models.IntegerField()
    basement = models.IntegerField()
    hotwaterheating = models.IntegerField()
    airconditioning = models.IntegerField()
    parking = models.IntegerField()
    prefarea = models.IntegerField()
    furnishingstatus = models.IntegerField()

    class Meta:
        verbose_name = "House Price"
        verbose_name_plural = "House Prices"

    def __str__(self):
        return f"House Price: {self.price}"