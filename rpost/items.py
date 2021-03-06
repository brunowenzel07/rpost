# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, Join, MapCompose
import unicodedata
import decimal

def processOR(value):
    if value == u"\u2014":
        return u'-'
    else:
        return value

def processTS(value):
    return value


def toascii(value):
    return value.encode('ascii', 'ignore')



# def gettotalprize(value):
#     if value is None:
#         return 0
#     else:
#         for p in value.split(', '):
#             newp = toascii(p)
#             ttl+= decimal.Decimal("".join(newp.split(",")))    
#         return ttl
#http://www.racingpost.com/horses/result_home.sd?race_id=618500&r_date=2015-02-27&popup=yes#results_top_tabs=re_&results_bottom_tabs=ANALYSIS

# class RpostHorseItem(scrapy.Item):
#     hdob =scrapy.Field()
#     hage = scrapy.Field()
#     hsex =scrapy.Field()
#     hcolor =scrapy.Field()
#     sire =scrapy.Field()
#     rpsireid =scrapy.Field()
#     dam =scrapy.Field()
#     rpdamid=scrapy.Field()
#     damsire = scrapy.Field()
#     rpdamsireid =scrapy.Field()
#     rptrainerid = scrapy.Field()
#     owner =scrapy.Field()
#     rpownerid = scrapy.Field()
#     breeder =scrapy.Field()
#     totalsales = scrapy.Field()



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
    raceratingspan = scrapy.Field()
    agerestriction = scrapy.Field()
    imperialdistance = scrapy.Field()
    going = scrapy.Field()
    prizemoney = scrapy.Field()
    prizecurrency = scrapy.Field()
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
    rphorseurl=scrapy.Field()
    horsename=scrapy.Field()
    horsenumber = scrapy.Field()
    draw = scrapy.Field()
    horsecountry=scrapy.Field()
    sp =scrapy.Field()
    actualwt=scrapy.Field()
    actualwt_dec=scrapy.Field()
    trainername=scrapy.Field()
    rpOR = scrapy.Field()
    rpTS= scrapy.Field()
    rpRPR=scrapy.Field()
    jockeyname=scrapy.Field()
    #ANALYSIS MUST BE LOGGED IN!!
    commentText=scrapy.Field()
    diomed = scrapy.Field()
    spotlight = scrapy.Field()
    #HORSE PAGE
    hdetails =scrapy.Field()
    gear = scrapy.Field()
    
    #STATS LAST RACE
    L1date= scrapy.Field()
    dayssincelastrunL1 = scrapy.Field()
    L1carriedwt= scrapy.Field()
    L1pos= scrapy.Field()
    L1comment= scrapy.Field()
    L1racetype = scrapy.Field()
    L1distance =scrapy.Field()
    L1goingcode = scrapy.Field()
    L1carriedwt = scrapy.Field()
    L1carriedwt_kg = scrapy.Field()
    L1gearchange = scrapy.Field()
    L1gear = scrapy.Field()
    L1sp = scrapy.Field()
    L1sp_dec = scrapy.Field()
    L1bf = scrapy.Field()
    L1runners = scrapy.Field()
    L1LBW = scrapy.Field()
    L1racedate = scrapy.Field()
    L2racedate = scrapy.Field()
    L3racedate = scrapy.Field()
    L4racedate = scrapy.Field()
    L5racedate = scrapy.Field()
    L6racedate = scrapy.Field()
    L1coursecode = scrapy.Field()
    L2coursecode = scrapy.Field()
    L3coursecode = scrapy.Field()
    L4coursecode = scrapy.Field()
    L5coursecode = scrapy.Field()
    L6coursecode = scrapy.Field()
    L1direction = scrapy.Field()
    L2direction = scrapy.Field()
    L3direction = scrapy.Field()
    L4direction = scrapy.Field()
    L5direction = scrapy.Field()
    L6direction = scrapy.Field()
    L2comment = scrapy.Field()
    L3comment = scrapy.Field()
    L4comment = scrapy.Field()
    L5comment = scrapy.Field()
    L6comment = scrapy.Field()
    L2commentN1 = scrapy.Field()
    L3commentN1 = scrapy.Field()
    L4commentN1 = scrapy.Field()
    L5commentN1 = scrapy.Field()
    L6commentN1 = scrapy.Field()
    L1pos = scrapy.Field()
    L2pos = scrapy.Field()
    L3pos = scrapy.Field()
    L4pos = scrapy.Field()
    L5pos = scrapy.Field()
    L6pos = scrapy.Field()
    L1prize = scrapy.Field()
    L2prize = scrapy.Field()
    L3prize = scrapy.Field()
    L4prize = scrapy.Field()
    L5prize = scrapy.Field()
    L6prize = scrapy.Field()
    L1racetype = scrapy.Field()
    L2racetype = scrapy.Field()
    L3racetype = scrapy.Field()
    L4racetype = scrapy.Field()
    L5racetype = scrapy.Field()
    L6racetype = scrapy.Field()
    form = scrapy.Field()
    avgspL6 = scrapy.Field()
    currentodds = scrapy.Field()
    L1prizemoneychange = scrapy.Field()
    avgpmL6 = scrapy.Field()
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

class RPostItemsLoader(ItemLoader):
    default_item_class = RpostResultsItem
    default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)
    racename_out = Compose(Join(), unicode, unicode.strip)
    racetime_out= Compose(Join(),unicode, unicode.strip)
    rpOR_out = Compose(TakeFirst(), unicode, unicode.strip, processOR) 
    rpTS_out = Compose(TakeFirst(), unicode, unicode.strip, processTS)
    prizemoney_out =Compose(TakeFirst(), unicode, unicode.strip, toascii)
    rphorseurl_out = Compose(TakeFirst(), unicode, unicode.strip)