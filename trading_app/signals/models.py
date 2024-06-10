# signals/models.py
from django.db import models

class Signal(models.Model):
    timestamp = models.TextField()  # Ensure this matches the database column type
    action = models.CharField(max_length=10)
    coin = models.CharField(max_length=10)
    price = models.FloatField()
    amount = models.FloatField()
    balance = models.FloatField()


    class Meta:
        db_table = 'signals'
        managed = False
