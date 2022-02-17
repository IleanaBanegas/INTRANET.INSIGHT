from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from .models import Profile, ProfileSerializer

# Create your views here.


class ProfileViewSet(viewsets.ModelViewSet):
  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer
