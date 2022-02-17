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
from threading import Timer


# Idioma "es-ES" (código para el español de España)
locale.setlocale(locale.LC_ALL, 'en_US.utf8') 
today = date.today()
d1 = today.strftime("%d-%b-%y")
# d1 = "15-Feb-21"
objDate = datetime.strptime(d1, '%d-%b-%y')
todayUnixDate = time.mktime(objDate.timetuple())

class GuatecomprasSpiders(scrapy.Spider):
    name = 'guatecompras_spiders'
    start_urls = ['https://www.guatecompras.gt/concursos/consultaConAvanz.aspx']
    custom_settings = {
        'FEED_URI': 'guatecompras_spiders.json',
        'FEED_FORMAT': 'json'
    }

    def parse(self, response):


        Timer(10.0, codes = response.xpath('//table[id="MasterGC_ContentBlockHolder_dgResultado"]//tr[@class="FilaTablaDetalle"]/td[@valign="top"]/div/div/a/text()').getall())


        yield {
            "codes": codes
        } 


        