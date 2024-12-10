from django.db import models
from django.contrib.auth.models import User

class Category(models.TextChoices):
    Plants='Plants'
    Seeds='Seeds'
    Pots='Pots'

class Product(models.Model):
    name = models.CharField(max_length=200, default='', blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=0)
    description = models.TextField(max_length=3000, default='', blank=False)
    Care_Guide = models.TextField(max_length=3000, default='', blank=True)  
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/%y/%m/%d')
    category = models.CharField(max_length = 40 , choices=Category.choices)

    def __str__(self):
        return self.name
