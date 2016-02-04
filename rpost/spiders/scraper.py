import scrapy
import re
from scrapy.contrib.spiders import Rule, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, Join, MapCompose
from scrapy.http import Request
from scrapy import log
import decimal
from .. import items
from rpost.items import RpostResultsItem
from datetime import datetime
import pprint
import logging
from time import sleep
from fractions import Fraction
import unicodedata
import numpy
# def getracetype(place):
#     racetypes = ['NvH', 'NHF', 'PTP', 'MdPTP', 'MdHntPTP', 'Hc', 'Md', '3yMd', 'MdAc']
#     if in racename 
        
#     else:
#         try:
#             return int(re.sub('\D', '', place))
#         except ValueError:
#             return None

def horselengthprocessor(value):
    #covers '' and '-'

    if '---' in value:
        return None
    elif value == '-':
        #winner
        return 0.0
    elif "-" in value and len(value) > 1:
        return float(Fraction(value.split('-')[0]) + Fraction(value.split('-')[1]))
    elif value == 'N':
        return 0.3
    elif value == 'SH':
        return 0.1
    elif value == 'HD':
        return 0.2
    elif value == 'SN':
        return 0.25  
    #nose?           
    elif value == 'NOSE':
        return 0.05
    elif '/' in value:
         return float(Fraction(value))        
    elif value.isdigit():
        return try_float(value)
    else:
        return None 


def parse_mixed_fraction(s):
    if s.isdigit():
        return float(s)
    elif len(s) == 1:
        return unicodedata.numeric(s[-1])
    else:
        return float(s[:-1]) + unicodedata.numeric(s[-1])

def sanitizelbw(lbw):
    if "L" not in lbw:
        '''suspect lbw'''
        return None
    lbw = lbw.replace("L", "")
    return parse_mixed_fraction(lbw)

#order is gear, SP
def parseL1gearSP(L1gearSP):
    if " " not in L1gearSP:
        return (None, None)
    elif len(L1gearSP.split(" ")) >1:
        return L1gearSP.split(" ")
    else:
        return (None, L1gearSP.split(" ")[0])

def distanetofurlongs(imperialdistance):
    pass

def isFavorite(winodds):
    if winodds is None:
        return None
    return "F" or "J" or "C" in winodds

def decimalizeodds(winodds):
    '''edge cases 9/4F EvensF '''
    if winodds is None:
        return None
    elif "Evens" in winodds:
        return 2.0
    else:
        #remove non digit chars not /
        winodds = winodds.replace("F", "").replace("J", "").replace("C", "")
        num, denom = winodds.split("/")
        dec = Fraction(int(num), int(denom)) + Fraction(1,1)
        return float(dec)


def isbeatenfavorite(winodds, place):
    return isFavorite(winodds) and place ==1

#imperialtofurlongs
def imperialtofurlongs(idist):
    '''ex 2m2f50y'''
    miles = 0
    furlongs = 0
    yards = 0
    if "f" in idist and "m" in idist:
        miles, furlongs = try_int(idist.split("m")[0]), try_int(idist.split("f")[0].split("m")[1])
    if "f" in idist and "m" not in idist:
        furlongs = try_int(idist.split("f")[0])
    return miles*8 + furlongs

def imperialweighttokg(imperialweight):
    '''stone ounces '''
    if "-" not in imperialweight or imperialweight is None:
        return None
    else:
        stones, pounds = imperialweight.split("-")
        return round( ((int(stones)*14)+int(pounds))/2.20462262, 0)



'''2m2f50y'''
def getdistance(distancegoing):
    '''2 cases: case1: has dot then decimal'''
    res = ""
    if '.' in distancegoing:
        d1 = ''.join( ''.join([ i for i in distancegoing.split(".")[0]if i.isdigit() ])   )
        d2 = ''.join( ''.join([ i for i in distancegoing.split(".")[1]if i.isdigit() ])   )
        res = d1 + '.' + d2
    else:
        res =''.join( ''.join([ i for i in distancegoing if i.isdigit() ])   )
    return res    


def tidytomoney(moneyvalue):
    from decimal import Decimal
    #replace non money chars
    if " " in moneyvalue:
        moneyvalue = moneyvalue.split(" ")[0]
    # ''.join( ''.join([ i for i in L1distgoing if not i.isdigit() ])) 
    newmoney = float(moneyvalue.replace(",", ""))
    return decimal.Decimal(newmoney)


def tf(values, encoding="utf-8"):
    value = ""
    for v in values:
        if v is not None and v != "":
            value = v
            break
    return value.encode(encoding).strip()

def removeunichars(value):
    return value.encode('ascii', 'ignore')

def cleandamsire(damsire):
    #count number of ( if 2 remove outer
    return damsire[1:-1]

def try_int(value):
    try:
        return int(value)
    except:
        return 0

def today():
    return datetime.today()

todaysdate = datetime.today()
todaysdatestr = datetime.today().strftime("%Y-%m-%d")
# from rpost.items import RpostResultsItem
class RPostItemsLoader(ItemLoader):
    default_item_class = RpostResultsItem
    default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)
    pm1_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm2_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm3_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm4_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm5_out = Compose(default_output_processor, removeunichars, tidytomoney)
    prizemoney_out = Compose(default_output_processor, removeunichars, tidytomoney)
    racename_out = Compose(default_output_processor, removeunichars)
    gear_out = Compose(default_output_processor, removeunichars)
    OR_out = Compose(default_output_processor, removeunichars)
    TS_out = Compose(default_output_processor, removeunichars)
    RPR_out = Compose(default_output_processor, removeunichars)
    damsire_out = Compose(default_output_processor, removeunichars, cleandamsire)
    jockeyname_out = Compose(default_output_processor, removeunichars)
    trainername_out = Compose(default_output_processor, removeunichars)
    sire_out = Compose(default_output_processor, removeunichars)
    dam_out = Compose(default_output_processor, removeunichars)
    horsename_out = Compose(default_output_processor, removeunichars)
    prizemoney_in = Compose(default_output_processor, removeunichars,tidytomoney)
    L1racedate = Compose(default_output_processor, removeunichars)
    L2racedate = Compose(default_output_processor, removeunichars)
    L3racedate = Compose(default_output_processor, removeunichars)
    L4racedate = Compose(default_output_processor, removeunichars)
    L5racedate = Compose(default_output_processor, removeunichars)
    L6racedate = Compose(default_output_processor, removeunichars)
    L1comment_out = Compose(default_output_processor, removeunichars)
    L2comment_out = Compose(default_output_processor, removeunichars)
    L3comment_out = Compose(default_output_processor, removeunichars)
    L4comment_out = Compose(default_output_processor, removeunichars)
    L5comment_out = Compose(default_output_processor, removeunichars)
    L6comment_out = Compose(default_output_processor, removeunichars)
    currentodds_out = Compose(default_output_processor, decimalizeodds)
#crawl spider with rules?

class RPracedaySpider(scrapy.Spider):
    name = "rpraceday"
    allowed_domains = ["www.racingpost.com"]
    #2015-03-03

    start_urls = ["http://www.racingpost.com/horses2/cards/home.sd?r_date=%s" % (todaysdate,)]

    def __init__(self):
        pass

    #TODO: fix currentodds, prizemoney decimalize  
    def parse(self, response):
        # if u"Today's Horse Racing Cards" not in response.body:
        #     log.msg("race card page not ready, waiting 2 secs", logLevel=log.INFO)
        #     sleep(2)
        #     yield Request(response.url, dont_filter=True)
        # else:
        #     #abandoned?
            nomeets =  response.xpath("count(//td[contains(@class,'meeting')])").extract()[0]
            if nomeets == 0:
                log.msg("race card page not ready, waiting 2 secs", logLevel=log.INFO)
                sleep(2)
                yield Request(response.url, dont_filter=True)
            else:
                for link in LinkExtractor(restrict_xpaths="//a[contains(@title,'View Card')]",).extract_links(response)[:-1]:
                    yield Request(link.url)
                l = RPostItemsLoader()
                items = list()
                # d = response.url.split("_")
                racedatematch = re.match(r'.*r_date=(\d\d\d\d-\d\d-\d\d)&.*', response.url)
                if racedatematch:
                    l.add_value('racedate', datetime.strptime(racedatematch.group(1), "%Y-%M-%d") )
                l.add_value('rpraceid',  re.match(r'.*race_id=(\d+).*', response.url).group(1))
                l.add_value('racetime', response.xpath("//span[@class='navRace']/span/text()").extract()[0])
                l.add_value('racecourse', response.xpath("//span[contains(@class,'placeRace')]/text()").extract()[0].strip() )
                theracecourse =l.get_collected_values('racecourse')[0]
                #exclude foreign courses
                if ("(IRE)" in theracecourse or "(AW)" in theracecourse) or theracecourse.count("(") ==0:
                    racename = response.xpath("//div[@class='info']/p/strong/strong[contains(@class,'uppercase')]/text()").extract()
                    l.add_value("racename", racename)
                    l.add_value('pm1', response.xpath("//ul[@class='results clearfix']/li/strong/text()").extract()[0])
                    
                    #race details
                    rd = response.xpath("//ul[@class='results clearfix']")
                    runners = rd.xpath("li[text()[contains(.,'Runners:')]]/strong/text()").extract()[0].strip()
                    l.add_value("runners", runners)
                    imperialdistance = rd.xpath("li[text()[contains(.,'Distance:')]]/strong/text()").extract()[0].strip()
                    l.add_value("imperialdistance", imperialtofurlongs(imperialdistance))
                    going = rd.xpath("li[text()[contains(.,'Going:')]]/strong/text()").extract()[0].strip()
                    l.add_value("going", going)
                    
                    #race conds

                    rc = response.xpath("//p[contains(@id,'raceConditionsText')]")
                    l.add_value("raceconditions", rc.xpath("/text()"))
                    l.add_value("prizemoney", rc.xpath("b/preceding-sibling::text()").extract())
                    l.add_value("pm2", rc.xpath("b[text()[contains(.,'2nd')]]/following-sibling::text()").extract() )
                    l.add_value("pm3", rc.xpath("b[text()[contains(.,'3rd')]]/following-sibling::text()").extract() )
                    l.add_value("pm4", rc.xpath("b[text()[contains(.,'4th')]]/following-sibling::text()").extract() )
                    l.add_value("pm5", rc.xpath("b[text()[contains(.,'5th')]]/following-sibling::text()").extract() )

                    # TABLE OF RUNNERS
                    rows = response.xpath("//table[@id='sc_horseCard']/tbody[contains(@id, 'sc_')]")
                    #for each horse

                    for row in rows:
                        # cr class
                        l.add_value("horsenumber",row.select("tr[contains(@class,'cr')]/td[@class='t']/strong/text()").extract())
                        l.add_value("draw",row.select("tr[contains(@class,'cr')]/td[@class='t']/sup/text()").extract())
                        l.add_value("horsename",row.select("tr[contains(@class,'cr')]/td[3]/a/b/text()").extract())
                        todaysgear = row.select("tr[contains(@class,'cr')]/td[3]/span/text()").extract()
                        l.add_value("gear", todaysgear)
                        horseurl = row.select("tr[contains(@class,'cr')]/td[3]/a/@href").extract()
                        l.add_value("rphorseid",horseurl[0].replace("&popup=1", "").split("=")[-1])

                        l.add_value("hage",row.select("tr[contains(@class,'cr')]/td[4]/text()").extract())
                        actualwt =row.select("tr[contains(@class,'cr')]/td[5]/div[1]/text()").extract()
                        l.add_value("actualwt",actualwt)
                        l.add_value("actualwt_dec", imperialweighttokg(actualwt))
                        l.add_value("OR",row.select("tr[contains(@class,'cr')]/td[5]/div[2]/text()").extract())
                        l.add_value("TS",row.select("tr[contains(@class,'cr')]/td[7]/text()").extract())
                        l.add_value("RPR",row.select("tr[contains(@class,'cr')]/td[8]/text()").extract())


                        # l.add_value("currentodds",row.select("tr[contains(@class,'cr')]/td[9]/button/div/div/text()").extract())
                        l.add_value("jockeyname",row.select("tr[contains(@class,'cr')]/td[6]/div[1]/a/text()").extract())
                        l.add_value("trainername",row.select("tr[contains(@class,'cr')]/td[6]/div[2]/a/text()").extract())
                        #2nd line
                        l.add_value("diomed",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='diomed']/text()").extract())
                        l.add_value("spotlight",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='spotlight']/text()").extract())
                        l.add_value("owner", row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='owners']/a/text()").extract())
                        ownerurl = row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='owners']/a/@href").extract()
                        l.add_value("rpownerid", ownerurl[0].replace("&popup=1", "").split("=")[-1])

                        #current odds

                        #TODO: enumrate based on number of previous runs ADD all data for each race up to 5
                            #previous form
                        lastrace = row.select("tr/td[contains(@class,'cardItemInfo')]/div[contains(@class,'forms')]")
                        # for item, tr in itertools.izip_longest(table_data, response.xpath("//table[@cellspacing=1 and @width='100%']//td[@rowspan=2]/..")):

                        # l.add_xpath("Sec%sDBL" % j, "./td[%s]/table/tr/td[2]/text()" % i)
                        if "There are no past perfomances on the Racing Post database for this horse" not in lastrace.xpath("text()").extract(): 
                            #positive terms in comments if associated with WINS PLACES NEXT GO!
                            
                            #use this to do MAX MIM AVG ad reqyured add to items field
                            ors = list()
                            tss = list()
                            rprs = list()
                            winningpms = list()  #prizemoneys fix so tha
                            finishes = dict()
                            sps = list()
                            daysoff = dict()   
                            noraces = lastrace.xpath("count(table/tr[not(@class='noSpace')])").extract()[0]
                            noraces = int(float(noraces))
                            todaysdate = l.get_collected_values("racedate")[0]
                            #TOD decimalize all prizemoneys and get average prizemoney last races
                            for i in range(2,2+noraces):
                                # thepos = try_int(lastrace.select("table/tr[%s]/td[5]/b[@class='black']/text()" % i).extract()[0])
                                #HORSES FAVORITE/HOME TRACK?
                                l.add_value("L%scoursecode" % str(i-1), lastrace.select("table/tr[%s]/td[3]/b[@class='black']/a/text()" % i).extract()[0])
                                directionpatt = re.compile("^.*(left|right)-handed.*")
                                thisdirection = lastrace.select("table/tr[%s]/td[3]/b[@class='black']/a/@title" % i).extract()
                                if thisdirection and re.match(directionpatt, thisdirection[0]):
                                    l.add_value("L%sdirection" % str(i-1), re.match(directionpatt, thisdirection[0]).group(1))      
                                l.add_value("L%sracedate" % str(i-1), datetime.strptime(lastrace.select("table/tr[%s]/td[2]/a/text()" % i).extract()[0], '%d%b%y'))
                                l.add_value("L%scomment" % str(i-1), lastrace.select("table/tr[%s]/td[5]/a/@title" % i).extract()[0])
                                l.add_value("L%spos" % str(i-1), try_int(lastrace.select("table/tr[%s]/td[5]/b[@class='black']/text()" % i).extract()[0]))
                                thispos = l.get_collected_values("L%spos" % str(i-1))[0]
                                thisprizemoney = l.get_collected_values("prizemoney")[0]
                                thisgearSP = lastrace.select("table/tr[%s]/td[5]/a/following-sibling::text()[1]" % i).extract()[0].strip()
                                thisgear, thissp = parseL1gearSP(thisgearSP)
                                # l.add_value("L%ssp" % str(i-1), decimalizeodds(thissp))
                                #non L1 sps, finishes go to dict- NOT Gear (Career)
                                if thissp:
                                    sps.append(decimalizeodds(thissp))
                                finishes["L%spos" % str(i-1)] = thispos #used for form calculations
                                thisdate = l.get_collected_values("L%sracedate" % str(i-1))[0]
                                daysoff["L%s" % str(i-1)] = (todaysdate-thisdate).days
                                lastracetypepm = lastrace.xpath("table/tr[%s]/td[3]/b/following-sibling::text()[1]" % i).extract()[0].strip()
                                l.add_value("L%sracetype" % str(i-1), re.match(r'^([A-Za-z0-9]*)\s*', lastracetypepm).group(1))
                                pmpatt = re.compile("^(.*)\s+(\d+)[kK]")
                                pmmatch = re.match(pmpatt, lastracetypepm)
                                if pmmatch:
                                    l.add_value("L%sprize" % str(i-1), pmmatch.group(2))
                                # lastracepm = lastracetyperacepm.split(" ")[1].replace("k", "").replace("K", "")
                                lastracepm = l.get_collected_values("L%sprize" % str(i-1))
                                if lastracepm and thispos == '1':
                                    #add pm from get collected values
                                    winningpms.append(int(lastracepm[0])*1000)
                                #TODAY vs. L1 comparisons here:
                                if i == 2:
                                    l.add_value("L%ssp" % str(i-1), decimalizeodds(thissp))
                                    l.add_value("L%sgear" % str(i-1), thisgear)
                                    if lastracepm:
                                        l.add_value("L%sprizemoneychange" % str(i-1), float(thisprizemoney) - float(int(lastracepm[0])*1000) )
                                    l.add_value("dayssincelastrunL1", (todaysdate-thisdate).days)
                                    l.add_value("L1gearchange", True if thisgear == todaysgear else False)

                                if thispos: 
                                    finishes["L%spos" % str(i-1)] = thispos
                                if i> 2:
                                    l.add_value("L%scommentN1" % str(i-1), finishes["L%spos" % str(i-2)])

                            #now compute averages for last runs
                            #WIN PLACE record this form go to database(also depends on racetype)
                            l.add_value("form", ''.join(['{}'.format(v) for k,v in sorted(finishes.iteritems())] ) )
                            l.add_value("avgspL6", round( numpy.mean(sps), 2))
                            l.add_value("avgpmL6", round( numpy.mean(winningpms), 2))
                            
                            # l.add_value("recentavgpm", round( numpy.mean(winningpms.values()), 2)) 

                            # L1date = lastrace.select("table/tr[2]/td[2]/a/text()")
                            # if L1date:
                            #     l.add_value("L1date", datetime.strptime(L1date.extract()[0], '%d%b%y'))
                            #     L1distgoing = lastrace.select("table/tr[2]/td[3]/b/a/following-sibling::text()[1]").extract()[0]
                            #     L1racetype = lastrace.select("table/tr[2]/td[3]/b/following-sibling::text()[1]").extract()[0]
                            # ###need to work on these two
                            #     l.add_value("L1distance", getdistance(L1distgoing))
                            #     l.add_value("L1goingcode", ''.join( ''.join([ i for i in L1distgoing if not i.isdigit() ])   ).replace(".", "") )
                            #     l.add_value("L1racetype",L1racetype)

                            #     L1carriedwt = lastrace.select("table/tr[2]/td[4]/text()").extract()[0]
                            #     l.add_value("L1carriedwt",L1carriedwt)
                            #     l.add_value("L1carriedwt_kg",   imperialweighttokg(L1carriedwt))
                            #     L1comment = lastrace.select("table/tr[2]/td[5]/a/@title").extract()[0]
                            #     l.add_value("L1comment", L1comment)
                            #     L1pos = try_int(lastrace.select("table/tr[2]/td[5]/b[@class='black']/text()").extract()[0])
                            #     l.add_value("L1pos", L1pos)
                            #     L1gearSP = lastrace.select("table/tr[2]/td[5]/a/following-sibling::text()[1]").extract()[0].strip()
                            #     L1gear, L1sp = parseL1gearSP(L1gearSP)
                            #     l.add_value("L1sp", L1sp)
                            #     l.add_value("L1gear", L1gear)
                            #     l.add_value("L1gearchange", True if L1gear == gear else False) 
                            #     l.add_value("L1sp_dec", decimalizeodds(L1sp))
                            #     l.add_value("L1bf", isbeatenfavorite(L1sp, L1pos))
                            #     L1LBW = lastrace.select("table/tr[2]/td[5]/a/text()")
                            #     l.add_value("L1LBW", sanitizelbw(L1LBW.extract()[0].split(" ")[0].replace('(', "")))
                            #     L1runners = lastrace.select("table/tr[2]/td[5]/b/following-sibling::text()[1]").extract()[0].replace('/', "")
                            #     l.add_value("L1runners", L1runners)


                                #ASSESSMENT OF L2, L3, L4, L5?
                        #TODO LBW decimalize L1pmz LOOK FOR CLASS DROPS L1, L1-L3 
                        # L2, L3 L4 L5 LBW pos odds (calculate in market), OR TS jumps avg RPR, Class 


                        #PEDIGREES
                        l.add_value("sire",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[1]/text()").extract())
                        sireurl = row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[1]/@href").extract()
                        l.add_value("rpsireid",sireurl[0].replace("&popup=1", "").split("=")[-1])
                        l.add_value("dam",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[2]/text()").extract())
                        damurl = row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[2]/@href").extract()
                        l.add_value("rpdamid",damurl[0].replace("&popup=1", "").split("=")[-1])
                        l.add_value("damsire",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[3]/text()").extract())
                        damsireurl = row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='pedigrees']/a[3]/@href").extract()
                        l.add_value("rpdamsireid",damsireurl[0].replace("&popup=1", "").split("=")[-1])
                # div class info p text = CLASS ageresrtiction
                        pprint.pprint(l.load_item())
                # TABLE sc_horseCard
                #horsenumber
                #horsename
                #gear
                #WT 
                #OR
                #jockey
                #trainer
                #TS
                #RPR
                # spotlightComment
                # diomedComment
                # button Class Click to bet next div = odds
                #betting forcast name of horse
                    #does population here
                        i = l.load_item()
                        items.append(i)
                # pprint.pprint(table_data)
                        yield i
            # yield l.load_item()
                    # return items

                

class RpostSpider(scrapy.Spider):
    name = "rpost"
    allowed_domains = ["www.racingpost.com"]
    start_url = "http://www.racingpost.com/horses2/results/home.sd?r_date=%s" #2015-03-01 %y-%m-%d
        # "http://www.racingpost.com/horses/result_home.sd?race_id=618500&r_date=2015-02-27&popup=yes#results_top_tabs=re_&results_bottom_tabs=ANALYSIS"


    #rules horses http://www.racingpost.com/horses/horse_home.sd?horse_id=871316
    def __init__(self, date=None):
        if date is None:
            raise ValueError("Invalid spider parameters")
        self.racedate = date
        # http://www.racingpost.com/horses2/cards/home.sd?r_date=2015-03-03

    def start_requests(self):
        return [Request(self.start_url % (self.racedate))]    


    def parse(self, response):
        # filename = response.url.split("/")[-2]
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        if "No race meeting" in response.body:
            log.msg("Results page not ready, waiting 2 secs...", logLevel=log.INFO)
            sleep(2)
            yield Request(response.url, dont_filter=True)
        else:
            for link in LinkExtractor(restrict_xpaths="//a[contains(@title,'View full result')]",).extract_links(response)[:-1]:
                yield Request(link.url)
            table_data = list()
            l = RPostItemsLoader()
            #FULL RESULTS PAGES    
            # Results From The 2.10 Race At Doncaster | 27 February 2015 | Racing Post</title>'
            title = response.xpath('//title').extract()
            d = response.url.split("_")
            l.add_value('racedate', ''.join([ i for i in d[-2] if i.isdigit()]))
            l.add_value('rpraceid', ''.join([ i for i in d[-1] if i.isdigit()]))
            racecourse = response.xpath('//title').extract()[0].split('|')[0].strip().split("At ")[-1]
            l.add_value('racecourse', racecourse)
            if u'(AW)' in racecouse: 
                l.add_value('surface', 'AWT')
            else:
                l.add_value('surface', 'Turf') 
            l.add_value('racetime', response.xpath('//title/text()').extract()[0].split('|')[0].strip().split(" Race")[0].replace("Results From The ", ""))
            # l.add_value('racename', response.xpath("//h3[@class='clearfix']/text()").extract()[0].strip())
            #race number?
            #race name, racetype

            racedetails = response.xpath("//div[@class='leftColBig']/ul/li/text()")
            l.add_value("raceclass", racedetails.extract()[0].split('\n')[1].replace("(", '').replace(")", "").strip())
            l.add_value("raceratingspan", racedetails.extract()[0].split('\n')[2].split(",")[0].replace("(", "").replace(")", "").strip())
            l.add_value("agerestriction", racedetails.extract()[0].split('\n')[2].split(")")[0].split(",")[-1].replace("(", "").strip())
            l.add_value("imperialdistance", racedetails.extract()[0].split('\n')[2].split(" ")[-1].replace("(", "").replace(")", ""))
            # item['racedate'] = ''.join([ i for i in d[-2] if i.isdigit()]) #yyyymmdd
            # item['rpraceid'] = ''.join([ i for i in d[-1] if i.isdigit()])

            # # response.xpath('//title').extract()[0].split('|')[0].strip()
            # item['racecourse'] = response.xpath('//title').extract()[0].split('|')[0].strip().split("At ")[-1]
            # item['racetime'] = response.xpath('//title/text()').extract()[0].split('|')[0].strip().split(" Race")[0].replace("Results From The ", "")

            # #raceinfo
            # race = response.xpath("//div[@class='leftColBig']").extract()
            # # racename = response.xpath("//div[@class='leftColBig']/h3/text()").extract()[0].strip()

            # # [u'', u' (Class 4) ', u' (0-105, 4yo+) (2m110y)', u' ', u' 2m\xbdf Good 8 hdles ']
            # response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')
            # item['raceclass'] = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[1].replace("(", '').replace(")", "").strip()

            # # u' (0-105, 4yo+) (2m110y)' ratingband agerestrictin (imperialdistance mfy)
            # racedata = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2]
            # item['ratingband'] = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(",")[0].replace("(", "").replace(")", "").strip()
            # item['agerestriction'] = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(")")[0].split(",")[-1].replace("(", "").strip()
            # item['imperialdistance'] = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(" ")[-1].replace("(", "").replace(")", "")
            pprint.pprint(l.load_item()) 
            # #prizemoney
            # prized = {}
            pm = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[1].split('\n')
            pms = [i.encode('ascii', 'ignore') for i in pm]
            pms2 = pms[0].split(', ')
            pms = [ decimal.Decimal(i.replace(',','')) for i in pms2]
            pms.sort() #inline
            for k, prize in enumerate(sorted(pms, reverse=True)):
                l.add_value('pm'+ str(k+1), prize)
                # prized[str(i+1)] = prize
            l.add_value('prizemoney', sum(pms))

            # #raceinfo
            ri = response.xpath("//div[@class='raceInfo']")
            l.add_value("runners", ri.xpath("b[text()[contains(.,'ran')]]/text()").extract()[0].strip().replace("ran", "").strip())
            l.add_value("paceinfo", ri.xpath("b[text()[contains(.,'TIME')]]/following-sibling::text()").extract()[0].strip() )
            #format 3m 58.40s (slow by 7.40s) '

            # #race analysis ALL text to racereport
            l.add_value("racereport", response.xpath("//div[@id='ANALYSIS']").extract()[0])

            i = l.load_item()
            table_data.append(i)

            for link in LinkExtractor(restrict_xpaths="//a[contains(@href,'horse_id')]/..", deny=( [r'.*/stallion/.*', r'.*/dam/.*' ]) ).extract_links(response):
                yield Request(link.url, callback=self.parse_horse, meta=dict(table_data=table_data))

        # yield item
            #the horses
            
            # for i, r in enumerate(response.xpath("//table/tbody")):
            #     #tds - blank horsenumber, lbw, horsename country sp (td span a), age, carrierWt, OR, TS , OPR,  RATED 
            #     #if * then not logged in!
            #     position
            #     lbw
            #     horse_id
            #     horsename
            #     horsecountry
            #     sp = winodds
            #     age
            #     weight
            #     trainername
            #     OR
            #     TS
            #     RPR
            #     jockeyname
            #     commentText

            
    def parse_horse(self, response):
        table_data = response.meta["table_data"]
        # item = items.RpostResultsItem()
        l = RPostItemsLoader()
        details = response.xpath("//ul[@id='detailedInfo']")
        hdetails= details.xpath("//li/b/text()").extract()[0].strip() #format u'4-y-o (19Apr11 b f)'
        # age = re.split('-y-o', details)
        date_string = re.split('-y-o', hdetails)[1].replace('(', "").replace(')', "").strip().split(' ')[0]
        
        hdob = datetime.strptime(date_string, '%d%b%y')
        hcolor = re.split('-y-o', hdetails)[1].replace('(', "").replace(')', "").strip().split(' ')[1]
        hsex = re.split('-y-o', hdetails)[1].replace('(', "").replace(')', "").strip().split(' ')[2]

        #convert to useful format from http://strftime.org/ 19Apr11 strftime %d%b%y datetime.strptime(date_string, '%d%b%y')
        
        
        l.add_value("hdob", hdob)
        l.add_value("hcolor", hcolor)
        l.add_value("hsex", hsex)
        # l.add_value("hdetails", details.xpath("//li/b/text()").extract()[0].strip())
        l.add_value("sire", details.xpath("//a[contains(@href,'stallionbook')]/text()").extract()[0].strip())
        l.add_value("dam", details.xpath("//a[contains(@href,'dam_home')]/text()").extract()[0].strip())
        # l.add_value("damsire", details.xpath("//a[contains(@href,'stallionbook')]/text()").extract()[0].strip())
        l.add_value("trainer", details.xpath("//a[contains(@href,'trainer_id')]/text()").extract()[0].strip())
        l.add_value("owner", details.xpath("//a[contains(@href,'owner_id')]/text()").extract()[0].strip())
        l.add_value("breeder",details.xpath("//li[text()[contains(.,'Breeder')]]/b/text()").extract()[0].strip())


        #SALES
        horse_sales  = response.xpath("//div[@id='horse_sales']/table")
        # if horse_sales:
            #get totals in PRICE COLUMN AND CURRENCY --> MONEY
            #field totalsales   

        yield l.load_item()


    # http://bloodstock.racingpost.com/stallionbook/stallion.sd?horse_id=96595&popup=1&tab=details    


# HORSE INFO 
# http://www.racingpost.com/horses/horse_home.sd?horse_id=740096#topHorseTabs=horse_race_record&bottomHorseTabs=horse_form
