from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Player(models.Model):
    image = models.ImageField(upload_to='players/', blank=True, null=True)
    name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField(unique=True)
    status = models.CharField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.jersey_number})"
