import scrapy
from tenders.models import Tender
from profiles.models import Profile
from django.contrib.auth.models import User
from webs.models import Web
from auth_user.models import Privilege
from countries.models import Country
import time
from datetime import date, datetime
from django.core.mail import send_mail
import locale

# Idioma "es-ES" (código para el español de España)
locale.setlocale(locale.LC_ALL, 'en_US.utf8')
today = date.today()
d1 = today.strftime("%d %b %Y")
objDate = datetime.strptime(d1, '%d %b %Y')
todayUnixDate = time.mktime(objDate.timetuple())


class IomSpiders(scrapy.Spider):
    name = 'iom_spiders'
    url = 'https://www.iom.int/procurement-opportunities'
    start_urls = [url]
    # custom_settings = {
    #     'FEED_URI': 'iom_spiders.json',
    #     'FEED_FORMAT': 'json'
    # }

    def parse(self, response):
        emails_users = []

        codes = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[1]/text()').getall()
        descriptions = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[2]/a/text()').getall()
        links = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[2]/a/@href').getall()
        places = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[9]/text()').getall()
        dates_posteds = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[7]/span/text()').getall()
        dates_deadline = response.xpath('//div[@class="view-content"]/table[2]/tbody/tr/td[8]/span/text()').getall()

        get_webs = Web.objects.all().filter(url=self.url)

        for item_get_webs in get_webs:
            get_countries = Country.objects.raw(f'SELECT * FROM countries_country WHERE id IN ({item_get_webs.countries_ids})')
            print('##########11', descriptions)

            for item in descriptions:
                print('##########22')
                objDate = datetime.strptime(
                    dates_posteds[descriptions.index(item)], '%d %b %Y')
                tenderUnixDate = time.mktime(objDate.timetuple())

                if todayUnixDate == tenderUnixDate:
                    print('##########33')
                    tender_counts = Tender.objects.filter(
                        description=descriptions[descriptions.index(item)],
                        publication_date=dates_posteds[descriptions.index(
                            item)]
                    ).values()
                    if len(tender_counts) <= 0:
                        print('##########44')
                        countriesIds_web = item_get_webs.countries_ids.upper().strip().split(',')

                        if len(countriesIds_web) > 0:
                            print('##########55')
                            validation = False
                            all_countries_in = any([item_country.name.upper(
                            ) in "TODOS LOS PAISES" for item_country in get_countries])
                            if all_countries_in:
                                print('##########66')
                                validation = True
                            else:
                                print('##########77')
                                country_in = any([item_country.name.upper() in places[descriptions.index(
                                    item)].upper() for item_country in get_countries])
                                if country_in:
                                    print('##########88')
                                    validation = True
                                else:
                                    print('##########99')
                                    description_in = any([item_country.name.upper() in descriptions[descriptions.index(
                                        item)].upper() for item_country in get_countries])
                                    if description_in:
                                        print('##########011')
                                        validation = True
                                    else:
                                        print('##########022')
                                        validation = False

                            if validation:
                                tenders_save = Tender(
                                    description=descriptions[descriptions.index(
                                        item)],
                                    code=codes[descriptions.index(item)],
                                    link=links[descriptions.index(item)],
                                    place_of_execution=places[descriptions.index(
                                        item)].rstrip(),
                                    publication_date=dates_posteds[descriptions.index(
                                        item)],
                                    closing_date=dates_deadline[descriptions.index(
                                        item)],
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
                                                            emails_users.append(
                                                                user.email)
                            else:
                                print('***** DONT SAVE *****')

        if len(emails_users) > 0:
            emails_users = set(emails_users)  # eliminar los correos duplicados
            print(emails_users)

            send_mail(
                'Nueva Licitaciones en Insight Intranet',
                f'El sistema ha registrado nuevas licitaciones de la página {self.url}',
                'insight@globaldigital-latam.com',
                emails_users,
            )
            print('***** SEND EMAIL *****')
