from django.db import models
from rest_framework import serializers

# Create your models here.


class Profile(models.Model):
  name = models.CharField(max_length=255)
  description = models.CharField(max_length=255)
  search_parameters = models.TextField(blank=True)
  discard_parameters = models.TextField(blank=True)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)


class ProfileSerializer(serializers.ModelSerializer):

  class Meta:
    model = Profile
    fields = ['id', 'name', 'description',
              'search_parameters', 'discard_parameters']
