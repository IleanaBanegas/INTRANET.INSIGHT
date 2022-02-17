import scrapy
from tenders.models import Tender
from profiles.models import Profile
from django.contrib.auth.models import User
from webs.models import Web
from auth_user.models import Privilege
from search_settings.models import SearchSettings
from django.core.mail import send_mail
import locale
import time
from datetime import date, datetime

# Idioma "es-ES" (código para el español de España)
locale.setlocale(locale.LC_ALL, 'es_ES.utf8') 
today = date.today()
d1 = today.strftime("%b %dº, %Y")
objDate = datetime.strptime(d1, '%b %dº, %Y')
todayUnixDate = time.mktime(objDate.timetuple())

class RdsEmpleosSpiders(scrapy.Spider):
    name = 'rds_empleados_spiders'
    start_urls = [
        'https://rds-empleos.hn/plazas/category/17'
    ]
    # custom_settings = {
    #     'FEED_URI': 'rds_empleados_spiders.json',
    #     'FEED_FORMAT': 'json'
    # }

    def parse(self, response):
        emails_users = []

        titles = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//h3/a/text()').getall()

        links_webs = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//h3/a/@href').getall()

        companies = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//p[not(contains(@class , "para"))]/text()').getall()

        descriptions = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//p[contains(@class, "para")]/text()').getall()

        places = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//ul[@class="featureInfo innerfeat"]/li[1]/text()').getall()

        dates = response.xpath('//ul[contains(@class, "listService")]//div[@class="listWrpService featured-wrap"]//ul[@class="featureInfo innerfeat"]/li[2]/text()').getall()

        get_webs = Web.objects.all().filter(url='https://rds-empleos.hn/plazas/category/17')

        for item_get_webs in get_webs:

            for item in titles:

                link = f"https://rds-empleos.hn/plazas/category/17/{links_webs[titles.index(item)]}"

                split_date = dates[titles.index(item)].split('-')

                objDate = datetime.strptime(split_date[0].strip(), "%b %dº, %Y")
                tenderUnixDate = time.mktime(objDate.timetuple())

                if todayUnixDate == tenderUnixDate:
                    tender_counts = Tender.objects.filter(
                        description=titles[titles.index(item)], 
                        publication_date=split_date[0].strip()
                    ).values()

                    if len(tender_counts) <= 0:
                        tenders_save = Tender(
                            countries_ids=item_get_webs.countries_ids,
                            description=titles[titles.index(item)], 
                            link=link, 
                            place_of_execution=places[titles.index(item)].rstrip(), 
                            awarning_authority=companies[titles.index(item)], 
                            publication_date=split_date[0].strip(), 
                            closing_date=split_date[1].strip(),
                            status="Nuevo"
                        )
                        tenders_save.save()
                        print('***** SAVE *****')

                        # buscar las direcciones de correo a enviar el email
                        userPrivileges = Privilege.objects.all()
                        for userPrivilege in userPrivileges:
                            countriesIds_privilege = userPrivilege.countries_ids.upper().strip().split(',')
                            if len(countriesIds_privilege) > 0:
                                for countryId_privilege in countriesIds_privilege:
                                    countriesIds_web = item_get_webs.countries_ids.upper().strip().split(',')
                                    if len(countriesIds_web) > 0:
                                        for countriesId_web in countriesIds_web:
                                            if countriesId_web.strip() == countryId_privilege.strip():
                                                users = User.objects.all().filter(id=userPrivilege.user_id)
                                                for user in users:
                                                    emails_users.append(user.email)

        if len(emails_users) > 0:
            emails_users = set(emails_users); #eliminar los correos duplicados
            print(emails_users)

            send_mail(
                'Nueva Licitaciones en Insight Intranet',
                'El sistema ha registrado nuevas licitaciones de la página https://rds-empleos.hn/plazas/category/17',
                'insight@globaldigital-latam.com',
                emails_users,
            )
            print('***** SEND EMAIL *****')
