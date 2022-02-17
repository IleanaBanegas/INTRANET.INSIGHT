import scrapy
import locale
import time
from django.contrib.auth.models import User
from tenders.models import Tender
from webs.models import Web
from countries.models import Country
from auth_user.models import Privilege
from datetime import date, datetime
from django.core.mail import send_mail

# Idioma "es-ES" (código para el ingles)
locale.setlocale(locale.LC_ALL, 'en_US.utf8')
today = date.today()
d1 = today.strftime("%B %d, %Y")
objDate = datetime.strptime(d1, '%B %d, %Y')
todayUnixDate = time.mktime(objDate.timetuple())


class IadbSpiders(scrapy.Spider):
    name = 'iadb_spiders'
    url = 'https://www.iadb.org/en/procurement-notices-search?query%5Bquery%5D=&query%5BprojectCountry%5D=&query%5Bproject_number%5D=&query%5BdateFrom_plan%5D=&query%5BdateTo_plan%5D=&query%5BNoticesType%5D=SPECIFIC&query%5BNotices%5D=CURRENT'
    start_urls = [url]

    def parse(self, response):
        emails_users = []

        descriptions = response.xpath(
            '//table[@class="table-links responsive-enabled"]/tbody/tr/td[3]/a/text()').getall()
        links = response.xpath(
            '//table[@class="table-links responsive-enabled"]/tbody/tr/td[3]/a/@href').getall()
        places = response.xpath(
            '//table[@class="table-links responsive-enabled"]/tbody/tr/td[2]/text()').getall()
        dates_posteds = response.xpath(
            '//table[@class="table-links responsive-enabled"]/tbody/tr/td[5]/text()').getall()
        dates_deadline = response.xpath(
            '//table[@class="table-links responsive-enabled"]/tbody/tr/td[6]/text()').getall()

        get_webs = Web.objects.all().filter(url=self.url)

        for item_get_webs in get_webs:
            print(item_get_webs)
            
            get_countries = Country.objects.raw(
                f'SELECT * FROM countries_country WHERE id IN ({item_get_webs.countries_ids})')

            for item in descriptions:
                objDate = datetime.strptime(dates_posteds[descriptions.index(item)], '%B %d, %Y')
                tenderUnixDate = time.mktime(objDate.timetuple())

                if todayUnixDate == tenderUnixDate:
                    tender_counts = Tender.objects.filter(
                        description=descriptions[descriptions.index(item)],
                        publication_date=dates_posteds[descriptions.index(item)]
                    ).values()
                    if len(tender_counts) <= 0:
                        countriesIds_web = item_get_webs.countries_ids.upper().strip().split(',')

                        if len(countriesIds_web) > 0:
                            validation = False
                            all_countries_in = any([item_country.name.upper(
                            ) in "TODOS LOS PAISES" for item_country in get_countries])
                            if all_countries_in:
                                validation = True
                            else:
                                country_in = any([item_country.name.upper() in places[descriptions.index(
                                    item)].upper() for item_country in get_countries])
                                if country_in:
                                    validation = True
                                else:
                                    description_in = any([item_country.name.upper() in descriptions[descriptions.index(
                                        item)].upper() for item_country in get_countries])
                                    if description_in:
                                        validation = True
                                    else:
                                        validation = False

                            if validation:
                                tenders_save = Tender(
                                    description=descriptions[descriptions.index(
                                        item)],
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
