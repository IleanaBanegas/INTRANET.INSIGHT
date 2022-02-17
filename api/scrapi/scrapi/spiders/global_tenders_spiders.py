import scrapy
import locale
import time
from tenders.models import Tender
from profiles.models import Profile
from webs.models import Web
from auth_user.models import Privilege
from countries.models import Country
from django.contrib.auth.models import User
from datetime import date, datetime
from django.core.mail import send_mail

# Idioma "en_US.utf8" (código para el ingles)
locale.setlocale(locale.LC_ALL, 'en_US.utf8')
today = date.today()
d1 = today.strftime("%d %b %Y")
objDate = datetime.strptime(d1, '%d %b %Y')
todayUnixDate = time.mktime(objDate.timetuple())


class GlobalTendersSpiders(scrapy.Spider):
    name = 'global_tenders_spiders'
    url = 'https://www.globaltenders.com/government-tenders-latin-america.php'
    start_urls = [url]

    def parse(self, response):
        emails_users = []

        descriptions = response.xpath('//div[@class="classWithPad"]/div[4]/div//table/tbody[2]/tr/td//tbody/tr[1]/td//tbody/tr/td[2]/text()').getall()
        places = response.xpath('//div[@class="classWithPad"]/div[4]/div//table/tbody[2]/tr/td//tbody/tr[3]/td//tbody/tr/td[2]/text()').getall()
        dates_deadline = response.xpath('//div[@class="classWithPad"]/div[4]/div//table/tbody[2]/tr/td//tbody/tr[4]/td//tbody/tr/td[4]/text()').getall()

        get_webs = Web.objects.all().filter(url = self.url)

        for item_get_webs in get_webs:
            get_countries = Country.objects.raw(f'SELECT * FROM countries_country WHERE id IN ({item_get_webs.countries_ids})')

            for item in descriptions:
                objDate = datetime.strptime(dates_deadline[descriptions.index(item)], '%d %b %Y')
                tenderUnixDate = time.mktime(objDate.timetuple())
                if todayUnixDate <= tenderUnixDate:
                    
                    tender_counts = Tender.objects.filter(description=descriptions[descriptions.index(item)]).values()
                    if len(tender_counts) <= 0:
                        countriesIds_web = item_get_webs.countries_ids.upper().strip().split(',')

                        if len(countriesIds_web) > 0:
                            validation = False
                            all_countries_in = any([item_country.name.upper() in "TODOS LOS PAISES" for item_country in get_countries])
                            if all_countries_in:

                                validation = True
                            else:
                                country_in = any([item_country.name.upper() in places[descriptions.index(
                                    item)].upper() for item_country in get_countries])
                                if country_in:
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
                                    place_of_execution=places[descriptions.index(item)].rstrip(),
                                    closing_date=dates_deadline[descriptions.index(item)],
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
