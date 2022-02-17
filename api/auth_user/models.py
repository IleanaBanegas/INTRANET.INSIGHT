from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


# Create your models here.


class Privilege(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='privilege')
    profiles_ids = models.CharField(max_length=255, blank=True)
    countries_ids = models.CharField(max_length=255, blank=True)
    tenders = models.BooleanField(default=True)
    webs = models.BooleanField(default=False)
    profiles = models.BooleanField(default=False)
    users = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)


class PrivilegeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Privilege
        fields = ['user', 'profiles_ids', 'countries_ids', 'tenders', 'webs', 'profiles', 'users', 'image']