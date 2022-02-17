from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from .models import Country, CountrySerializer

# Create your views here.


class CountryViewSet(viewsets.ModelViewSet):
  queryset = Country.objects.all()
  serializer_class = CountrySerializer
