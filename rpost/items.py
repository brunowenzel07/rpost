# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#http://www.racingpost.com/horses/result_home.sd?race_id=618500&r_date=2015-02-27&popup=yes#results_top_tabs=re_&results_bottom_tabs=ANALYSIS
class RpostItem(scrapy.Item):
    # define the fields for your item here like:
    racecourse = scrapy.Field()
    racenumber = scrapy.Field()
    pass
