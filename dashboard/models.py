from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)