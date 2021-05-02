from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Profile(models.Model):
    bacnet_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=64)
    gender = models.CharField(max_length=6, blank=True, null=True, default=None)
    birthday = models.DateField(blank=True, null=True, default=None)
    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    town = models.CharField(max_length=64, blank=True, null=True, default=None)
    language = models.CharField(max_length=256, blank=True, null=True, default=None) #https://stackoverflow.com/questions/22340258/django-list-field-in-model
    profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.name} Profile / {self.bacnet_id}'