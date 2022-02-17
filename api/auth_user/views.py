from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Privilege, PrivilegeSerializer


class AuthUserViewSet(viewsets.ViewSet):

  @action(methods=['post'], detail=False, url_path='login-user', url_name='login_user')
  def login(self, request, pk=None):

    email = request.data['email']
    password = request.data['password']

    user_auth = User.objects.filter(email=email)
    print(user_auth)

    return Response(user_auth)

class PrivilegeViewSet(viewsets.ModelViewSet):
  queryset = Privilege.objects.all()
  serializer_class = PrivilegeSerializer

  @action(methods=['get'], detail=False, url_path='privilege-user/(?P<user_id>\d+)', url_name='privilege-user')
  def privilegeUser(self, request, user_id):
    privilege = self.queryset.get(user=user_id)

    if privilege.id:
      data_json = {
        'id': privilege.id,
        'tenders': privilege.tenders,
        'webs': privilege.webs,
        'profiles': privilege.profiles,
        'users': privilege.users,
        'image': privilege.image,
        'countries_ids': privilege.countries_ids,
        'profiles_ids': privilege.profiles_ids,
      }
      return Response(data_json)
