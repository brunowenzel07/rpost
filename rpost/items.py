# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#http://www.racingpost.com/horses/result_home.sd?race_id=618500&r_date=2015-02-27&popup=yes#results_top_tabs=re_&results_bottom_tabs=ANALYSIS
class RpostResultsItem(scrapy.Item):
    # RACE SPECIFIC INFO
    racecourse = scrapy.Field()
    racenumber = scrapy.Field()
    racedate = scrapy.Field()
    rpraceid = scrapy.Field()
    racetime = scrapy.Field()
    rpraceid = scrapy.Field()
    racecourse = scrapy.Field()
    racename = scrapy.Field()
    racetype = scrapy.Field()
    raceclass = scrapy.Field()
    raceconditions = scrapy.Field()
    ratingband = scrapy.Field()
    agerestriction = scrapy.Field()
    imperialdistance = scrapy.Field()
    going = scrapy.Field()
    totalpm = scrapy.Field()
    pmcurr = scrapy.Field()
    pm1 = scrapy.Field()
    pm2 = scrapy.Field()
    pm3 = scrapy.Field()
    pm4 = scrapy.Field()
    pm5 = scrapy.Field()
    pm6 = scrapy.Field()
    pm7 = scrapy.Field()
    pm8 = scrapy.Field()
    pm9 = scrapy.Field()
    runners = scrapy.Field()
    paceinfo = scrapy.Field() #string
    racereport = scrapy.Field()
    #RUNNER RESULTS TABLE:
    position=scrapy.Field()
    lbw=scrapy.Field()
    rphorseid=scrapy.Field()
    horsename=scrapy.Field()
    horsenumber = scrapy.Field()
    draw = scrapy.Field()
    horsecountry=scrapy.Field()
    sp =scrapy.Field()
    weight=scrapy.Field()
    trainername=scrapy.Field()
    OR = scrapy.Field()
    TS= scrapy.Field()
    RPR=scrapy.Field()
    jockeyname=scrapy.Field()
    #ANALYSIS MUST BE LOGGED IN!!
    commentText=scrapy.Field()
    diomed = scrapy.Field()
    spotlight = scrapy.Field()
    #HORSE PAGE
    hdetails =scrapy.Field()
    hdob =scrapy.Field()
    hage = scrapy.Field()
    hsex =scrapy.Field()
    hcolor =scrapy.Field()
    sire =scrapy.Field()
    rpsireid =scrapy.Field()
    dam =scrapy.Field()
    rpdamid=scrapy.Field()
    damsire = scrapy.Field()
    rpdamsireid =scrapy.Field()
    rptrainerid = scrapy.Field()
    owner =scrapy.Field()
    rpownerid = scrapy.Field()
    breeder =scrapy.Field()
    totalsales = scrapy.Field()
    #STATS LAST RACE
    L1date= scrapy.Field()
    L1carriedwt= scrapy.Field()
    L1pos= scrapy.Field()
    L1comment= scrapy.Field()
    L1racetype = scrapy.Field()
    L1distance =scrapy.Field()
    L1goingcode = scrapy.Field()
    L1carriedwt = scrapy.Field()
    L1SP = scrapy.Field()
    L1runners = scrapy.Field()