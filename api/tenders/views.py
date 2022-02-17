from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from .models import Tender, TenderSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, authentication
from django.http import HttpResponse
from django.db.models.functions import Lower


# Create your views here.


class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all().order_by(Lower('created').desc())
    serializer_class = TenderSerializer
   
    @action(methods=['get'], detail=False, url_path='tender-users', url_name='tender-users')
    def tenderUsers(self, request, pk=None):
        print(request.user, request.auth, '*' * 10)
        return Response('ERROR CON LOS DATOS', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='update-status', url_name='update-status')
    def updateStatus(self, request, pk=None):
        t = Tender.objects.get(id = request.data["id"])
        t.status = request.data["status"]
        t.save()
        # print(request.data["id"], '*' * 10, t)
        return Response({'status':t.status})
