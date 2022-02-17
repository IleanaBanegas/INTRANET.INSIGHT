import scrapy


class UngmSpiders(scrapy.Spider):
    name = 'ungm_spiders'
    start_urls = [
        'https://www.ungm.org/Public/Notice?agencyEnglishAbbreviation=UNOPS'
    ]

    def parse(self, response):
        descriptions = response.xpath(
            '//div[@id="tblNotices"]/div[2]/div/div[2]/div/div/span/text()'
        ).getall()
        print('################################################################')
        print(descriptions)
