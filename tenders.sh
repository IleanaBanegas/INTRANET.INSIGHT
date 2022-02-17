#!/bin/bash

cd /var/www/insightIntranet/api
PATH=$PATH:/usr/local/bin
export PATH
source .env/bin/activate
cd scrapi
scrapy crawl acnur_spiders && scrapy crawl bcies_spiders && scrapy crawl global_tenders_spiders && scrapy crawl iom_spiders && scrapy crawl rds_empleados_spiders && scrapy crawl undp_spiders && scrapy crawl iadb_spiders