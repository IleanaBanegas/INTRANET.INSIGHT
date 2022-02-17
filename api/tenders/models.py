from django.db import models
from rest_framework import serializers
from countries.models import Country
from profiles.models import Profile
from django.contrib.auth.models import User

# Create your models here.


class Tender(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # country = models.ForeignKey(Country, on_delete=models.CASCADE)
    # profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    description = models.TextField()
    code = models.CharField(max_length=255, blank=True)
    place_of_execution = models.CharField(max_length=255, blank=True)
    awarning_authority = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    tender_viewed = models.BooleanField(default=False)

    publication_date = models.CharField(max_length=255, blank=True)
    closing_date = models.CharField(max_length=255, blank=True)
    countries_ids = models.CharField(max_length=255, blank=True)
    # dates = models.CharField(max_length=255, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=100, blank=True)


class TenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tender
        fields = ['id', 'description', 'code', 'place_of_execution',
                  'awarning_authority', 'link', 'tender_viewed', 'publication_date', 'closing_date', 'countries_ids']
