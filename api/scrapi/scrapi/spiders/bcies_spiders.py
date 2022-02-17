import scrapy
from tenders.models import Tender
from profiles.models import Profile
from django.contrib.auth.models import User
from webs.models import Web
from auth_user.models import Privilege
from search_settings.models import SearchSettings
import time
from datetime import date, datetime
from django.core.mail import send_mail

today = date.today()
d1 = today.strftime('%d/%m/%Y')
objDate = datetime.strptime(d1, '%d/%m/%Y')
todayUnixDate = time.mktime(objDate.timetuple())

class BciesSpiders(scrapy.Spider):
    name = 'bcies_spiders'
    start_urls = [
        'https://adquisiciones.bcie.org/avisos-de-adquisicion'
    ]
    # custom_settings = {
    #     'FEED_URI': 'bcies_spiders.json',
    #     'FEED_FORMAT': 'json'
    # }

    def parse(self, response):
        emails_users = []

        codes = response.xpath('//table[@id="customtables"]//tbody/tr/td[1]/text()').getall()

        titles = response.xpath('//table[@id="customtables"]//tbody/tr/td[2]/a/text()').getall()

        links_webs = response.xpath('//table[@id="customtables"]//tbody/tr/td[2]/a/@href').getall()

        places = response.xpath('//table[@id="customtables"]//tbody/tr/td[3]/text()').getall()

        dates1 = response.xpath('//table[@id="customtables"]//tbody/tr/td[4]/text()').getall()

        dates2 = response.xpath('//table[@id="customtables"]//tbody/tr/td[5]/text()').getall()

        get_webs = Web.objects.all().filter(url='https://adquisiciones.bcie.org/avisos-de-adquisicion')

        for item_get_webs in get_webs:
            
            for item in dates1:
                           
                link = f'{links_webs[dates1.index(item)]}'

                objDate = datetime.strptime(dates1[dates1.index(item)].strip(), '%d/%m/%Y')
                tenderUnixDate = time.mktime(objDate.timetuple())

                if todayUnixDate == tenderUnixDate:
                    tender_counts = Tender.objects.filter(
                        description=titles[dates1.index(item)], 
                        publication_date=dates1[dates1.index(item)].strip()
                    ).values()

                    if len(tender_counts) <= 0:
                        tenders_save = Tender(
                            countries_ids=item_get_webs.countries_ids, 
                            description=titles[dates1.index(item)], 
                            code=codes[dates1.index(item)], 
                            link=link, 
                            place_of_execution=places[dates1.index(item)].rstrip(), 
                            publication_date=dates1[dates1.index(item)].strip(), 
                            closing_date=dates2[dates1.index(item)].strip(),
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
                'El sistema ha registrado nuevas licitaciones de la página https://adquisiciones.bcie.org/avisos-de-adquisicion',
                'insight@globaldigital-latam.com',
                emails_users,
            )
            print('***** SEND EMAIL *****')
