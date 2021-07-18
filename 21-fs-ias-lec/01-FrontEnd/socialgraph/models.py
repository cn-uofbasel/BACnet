__author__ = "Philipp Haller, Pascal Kunz, Sebastian Schlachter"
'''This file defines all models and there functions in the used database.'''

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
import datetime

class Status(models.Model):
    """This is needed to create multiple instances of status, one Profile can then have a relation to multiple
    status (The Current and all the old ones)."""
    timestamp = models.DateTimeField(blank=True, null=True, default=None)
    status = models.CharField(max_length=256, blank=True, null=True, default=None)


class Profile(models.Model):
    """Each entry stores the information of one nodes/users Profile Page."""
    bacnet_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    gender = models.CharField(max_length=6, blank=True, null=True, default=None)
    birthday = models.DateField(blank=True, null=True, default=None)
    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    town = models.CharField(max_length=64, blank=True, null=True, default=None)
    language = models.CharField(max_length=256, blank=True, null=True, default=None)
    profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics')
    myself = models.BooleanField(default=False)
    node_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=256, blank=True, null=True, default=None)
    follows = models.ManyToManyField('self', symmetrical=False)
    status_list = models.ManyToManyField(Status, symmetrical=False)
    influencer = models.BooleanField(default=False)

    def __str__(self):
        """Defines the string representation"""
        return f'{self.name} Profile / {self.bacnet_id}'

    def get_details(self):
        """Returns a hashmap containing the attributes (of this database entry) that should be displayed on the profile
        page. """
        details = {}
        if self.gender is not None:
            details['Gender']= self.gender
        if self.birthday is not None:
            details['Birthday']= self.birthday
        if self.country is not None:
            details['Country']= self.country
        if self.town is not None:
            details['Town']= self.town
        if self.language is not None:
            details['Language']= self.language
        return details

class FollowRecommendations(models.Model):
    layer = models.IntegerField(default=None)
    bacnet_id = models.CharField(max_length=64, primary_key=True)
    id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    gender = models.CharField(max_length=6, blank=True, null=True, default=None)
    birthday = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=None)
    influencer = models.BooleanField(blank=True, null=True, default=None)
    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    town = models.CharField(max_length=64, blank=True, null=True, default=None)
    language = models.CharField(max_length=256, blank=True, null=True,
                                default=None)
    profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics')
    levenshteinDistName = models.IntegerField(default=None)
    levenshteinDistTown = models.IntegerField(default=None)


