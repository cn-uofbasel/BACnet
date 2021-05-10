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

    def get_details(self):
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
    name = models.CharField(max_length=64)
    gender = models.CharField(max_length=6, blank=True, null=True, default=None)
    birthday = models.DateField(blank=True, null=True, default=None)
    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    town = models.CharField(max_length=64, blank=True, null=True, default=None)
    language = models.CharField(max_length=256, blank=True, null=True,
                                default=None)  # https://stackoverflow.com/questions/22340258/django-list-field-in-model
    profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics')

    @classmethod
    def create(cls, layerNode, bacnet_idNode, nameNode,
               genderNode, birthdayNode, countryNode,
               townNode, languageNode, profile_picNode):
        recommendation = cls(layer = layerNode, bacnet_id = bacnet_idNode, name = nameNode,
                    gender = genderNode, birthday = birthdayNode, country = countryNode,
                    town = townNode, language = languageNode, profile_pic = profile_picNode)
        return recommendation


    def __str__(self):
        return f'{self.name} Profile / {self.bacnet_id}'

    def get_details(self):
        details = {}
        if (self.layer < 3):
            details['layer'] = self.layer
            if self.gender is not None:
                details['Gender'] = self.gender
            if self.birthday is not None:
                details['Birthday'] = self.birthday
            if self.country is not None:
                details['Country'] = self.country
            if self.town is not None:
                details['Town'] = self.town
            if self.language is not None:
                details['Language'] = self.language
        return details

