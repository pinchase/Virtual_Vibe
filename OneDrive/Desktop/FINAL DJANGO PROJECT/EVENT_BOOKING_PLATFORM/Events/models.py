from django.db import models
import datetime

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price field
    description = models.TextField()

class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Link to Event
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    number_of_tickets = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='total_price')
    # booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.event.name} - {self.number_of_tickets} tickets"