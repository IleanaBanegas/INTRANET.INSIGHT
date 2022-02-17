from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from .models import SearchSettings, SearchSettingSerializer

# Create your views here.


class SearchSettingViewSet(viewsets.ModelViewSet):
  queryset = SearchSettings.objects.all()
  serializer_class = SearchSettingSerializer
