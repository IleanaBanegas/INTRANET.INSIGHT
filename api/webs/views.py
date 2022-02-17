from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from .models import Web, WebSerializer

# Create your views here.


class WebViewSet(viewsets.ModelViewSet):
  queryset = Web.objects.all()
  serializer_class = WebSerializer
