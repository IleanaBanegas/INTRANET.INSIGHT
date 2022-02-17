import scrapy
from tenders.models import Tender
from profiles.models import Profile
from django.contrib.auth.models import User
from webs.models import Web
from auth_user.models import Privilege
from countries.models import Country
from django.core.mail import send_mail
import locale
import time
from datetime import date, datetime

# Idioma "es-ES" (código para el español de España)
locale.setlocale(locale.LC_ALL, 'es_ES.utf8') 
today = date.today()
d1 = today.strftime("%d %b %Y")
objDate = datetime.strptime(d1, '%d %b %Y')
todayUnixDate = time.mktime(objDate.timetuple())

class AcnurSpiders(scrapy.Spider):
    name = 'acnur_spiders'
    url = 'https://www.acnur.org/search' 
    start_urls = [url]

    def parse(self, response):
        emails_users = []

        descriptions = response.xpath('//div[@class="section__wrapper"]/ul[@class="results"]/li/a/h2/text()').getall()
        links = response.xpath('//div[@class="section__wrapper"]/ul[@class="results"]/li/a/@href').getall()
        dates_posteds = response.xpath('//div[@class="section__wrapper"]/ul[@class="results"]/li/a/span[@class="date--type"]/text()').getall()

        get_webs = Web.objects.all().filter(url=self.url)

        for item_get_webs in get_webs:
            get_countries = Country.objects.raw(f'SELECT * FROM countries_country WHERE id IN ({item_get_webs.countries_ids})')
            
            for item in descriptions:
                objDate = datetime.strptime(dates_posteds[descriptions.index(item)].strip().lower(), '%d %b %Y')
                tenderUnixDate = time.mktime(objDate.timetuple())

                if todayUnixDate == tenderUnixDate:
                    tender_counts = Tender.objects.filter(description=descriptions[descriptions.index(item)]).values()

                    if len(tender_counts) <= 0:
                        countriesIds_web = item_get_webs.countries_ids.upper().strip().split(',')

                        if len(countriesIds_web) > 0:
                            validation = False
                            all_countries_in = any([item_country.name.upper() in "TODOS LOS PAISES" for item_country in get_countries])
                            if all_countries_in:
                                validation = True
                            else:
                                description_in = any([item_country.name.upper() in descriptions[descriptions.index(item)].upper() for item_country in get_countries])
                                if description_in:
                                    validation = True
                                else:
                                    validation = False
                                
                            if validation:
                                tenders_save = Tender(
                                    description=descriptions[descriptions.index(item)], 
                                    link=links[descriptions.index(item)], 
                                    publication_date=dates_posteds[descriptions.index(item)].strip(), 
                                    status="0"
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
                            else:
                                print('***** DONT SAVE *****')

        if len(emails_users) > 0:
            emails_users = set(emails_users) #eliminar los correos duplicados
            print(emails_users)

            send_mail(
                'Nueva Licitaciones en Insight Intranet',
                f'El sistema ha registrado nuevas licitaciones de la página {self.url}',
                'insight@globaldigital-latam.com',
                emails_users,
            )
            print('***** SEND EMAIL *****')
