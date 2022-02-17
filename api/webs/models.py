from django.db import models
from rest_framework import serializers
from countries.models import Country
from django.db.models.signals import post_save
from django.core.mail import send_mail


# Create your models here.
class Web(models.Model):
  name = models.CharField(max_length=255)
  url = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  note = models.TextField(blank=True)
  status = models.BooleanField(default=False)
  countries_ids = models.CharField(max_length=255, blank=True)

  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)


class WebSerializer(serializers.ModelSerializer):
  # country = CountrySerializer(many=False)

  class Meta:
    model = Web
    fields = ['id', 'name', 'url', 'status', 'description', 'note', 'countries_ids']


# def send_notification(sender, **kwargs):
#   if kwargs['created']:
#     item = kwargs['instance']

#     send_mail(
#       'Nuevo Url Agregada en Insight Intranet',
#       f"Por favor configurar la siguiente Url {item.url}. Recuerde que luego de configurar se debe cambiar el estado de la misma.",
#       'insight@globaldigital-latam.com',
#       ['leonardo@apreciasoft.com', 'jgam310@hotmail.com'],
#     )

#     print('***** SEND EMAIL *****')

# post_save.connect(send_notification, sender=Web)