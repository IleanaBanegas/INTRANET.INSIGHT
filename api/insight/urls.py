"""insight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User

from rest_framework import routers, serializers, viewsets
from django.core import serializers as serializers_django

from webs.views import WebViewSet
from countries.views import CountryViewSet
from countries.models import Country
from profiles.views import ProfileViewSet
from profiles.models import Profile
from tenders.views import TenderViewSet
from tenders.models import Tender
from auth_user.views import AuthUserViewSet, PrivilegeViewSet
from auth_user.models import PrivilegeSerializer, Privilege

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse


# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email',
                  'is_staff', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    """
    Authentication is needed for this methods
    """
    authentication_classes = (TokenAuthentication,)

    @action(methods=['get'], detail=False, url_path='tender-users', url_name='tender-users')
    def tenderUsers(self, request, pk=None):
        user_auth = self.queryset.get(username=request.user)

        if user_auth.id:
            tenders = Tender.objects.values().order_by('-id')
            privilege = Privilege.objects.filter(user_id=user_auth.id).get()
            
            privilege_countriesIds = privilege.countries_ids.upper().strip().split(',')
            privilege_profilesIds = privilege.profiles_ids.upper().strip().split(',')

            # si es administrador se le muestran todas las licitaciones o si tiene relacionado todos los paises
            if "241" in privilege_countriesIds or user_auth.is_staff:
                return JsonResponse({"tenders": list(tenders)})
            else:
                countries = Country.objects.raw(f'SELECT * FROM countries_country WHERE id IN ({privilege.countries_ids.strip()})')
                response = []

                for tender in tenders:
                    country_in = any([country.name.upper() in tender['place_of_execution'].upper() for country in countries]) 
                    aux_description = tender['description'].upper() # variable auxiliar para la descripcion
                    validation = False
                    if (aux_description != ''): # chequeo que description sea distinto a vacio
                        if country_in:
                            validation = True
                        else:
                            description_in = any([country.name.upper() in aux_description for country in countries])
                            if description_in:
                                validation = True
                            else:
                                validation = False

                        if validation:
                            for profileId_privilege in privilege_profilesIds:
                                profile = Profile.objects.filter(id=profileId_privilege).get()
                                words_searchs = profile.search_parameters.upper().strip().split(',')
                                word_key_in = any([words_search in aux_description for words_search in words_searchs])

                                if word_key_in:
                                    if profile.discard_parameters:
                                        words_not_searchs = profile.discard_parameters.upper().strip().split(',')
                                        word_key_not_in = any([words_not_search in aux_description for words_not_search in words_not_searchs])

                                        if word_key_not_in:
                                            print('***** NOT SHOW *****')
                                        else:
                                            response.append(tender)
                                    else:
                                        response.append(tender)

                return JsonResponse({"tenders": list(response)})

    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login(self, request, pk=None):

        email = request.data['email']
        password = request.data['password']
        user_auth = self.queryset.filter(email=email).get()

        if user_auth.password == password:
            token, created = Token.objects.get_or_create(user=user_auth)
            privilege = Privilege.objects.filter(user_id=user_auth.id).get()

            user_json = {
                'id': user_auth.id,
                'is_staff': user_auth.is_staff,
                'last_name': user_auth.last_name,
                'first_name': user_auth.first_name,
                'token': token.key,
                'privilege_tenders': privilege.tenders,
                'privilege_webs': privilege.webs,
                'privilege_profiles': privilege.profiles,
                'privilege_users': privilege.users,
                'image': privilege.image,
            }
            return Response(user_json)
        else:
            return Response('ERROR CON LOS DATOS', status=status.HTTP_400_BAD_REQUEST)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'webs', WebViewSet)
router.register(r'profiles', ProfileViewSet)
# router.register(r'search_settings', SearchSettingViewSet)
router.register(r'tenders', TenderViewSet)
router.register(r'privileges', PrivilegeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
