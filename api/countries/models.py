from django.db import models
from rest_framework import serializers

# Create your models here.


class Country(models.Model):
  name = models.CharField(max_length=255)
  code = models.CharField(max_length=10)


class CountrySerializer(serializers.HyperlinkedModelSerializer):

  class Meta:
    model = Country
    fields = ['id', 'name', 'code']