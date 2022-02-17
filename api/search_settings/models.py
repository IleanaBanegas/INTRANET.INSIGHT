from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import User
from countries.models import Country
from profiles.models import Profile

# Create your models here.


class SearchSettings(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  country = models.ForeignKey(Country, on_delete=models.CASCADE)
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)


class SearchSettingSerializer(serializers.ModelSerializer):
  # country = CountrySerializer(many=False)

  class Meta:
    model = SearchSettings
    fields = ['id', 'user', 'country', 'profile']
