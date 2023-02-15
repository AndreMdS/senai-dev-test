from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Occurrence(models.Model):
    occurrence_id = models.AutoField(primary_key=True)
    mac_address = models.CharField(max_length=17)
    occurrence_time = models.DateTimeField()
    object_class = models.CharField(max_length=15)
    evidence_url = models.CharField(max_length=1000)

class User(AbstractUser):
    REQUIRED_FIELDS = ['password']
    USERNAME_FIELD = 'username'
