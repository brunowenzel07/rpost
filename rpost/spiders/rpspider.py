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


# def getracetype(place):
#     racetypes = ['NvH', 'NHF', 'PTP', 'MdPTP', 'MdHntPTP', 'Hc', 'Md', '3yMd', 'MdAc']
#     if in racename 
        
#     else:
#         try:
#             return int(re.sub('\D', '', place))
#         except ValueError:
#             return None

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
    return ''.join([ i for i in moneyvalue if i.isdigit()])


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

todaysdate = datetime.today().strftime("%Y-%m-%d")
# from rpost.items import RpostResultsItem
class RPostItemsLoader(ItemLoader):
    default_item_class = RpostResultsItem
    default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)
    pm1_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm2_out = Compose(default_output_processor, removeunichars, tidytomoney)
    pm3_out = Compose(default_output_processor, removeunichars)
    pm4_out = Compose(default_output_processor, removeunichars)
    pm5_out = Compose(default_output_processor, removeunichars)
    totalpm_out = Compose(default_output_processor, removeunichars, tidytomoney)
    OR_out = Compose(default_output_processor, removeunichars)
    damsire_out = Compose(default_output_processor, removeunichars, cleandamsire)
#crawl spider with rules?

class RPracedaySpider(scrapy.Spider):
    name = "rpraceday"
    allowed_domains = ["www.racingpost.com"]
    #2015-03-03

    start_urls = ["http://www.racingpost.com/horses2/cards/home.sd?r_date=%s" % (todaysdate,)]

    def __init__(self):
        pass

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

                # d = response.url.split("_")
                l.add_value('racedate', todaysdate)
                # l.add_value('rpraceid', ''.join([ i for i in d[-1] if i.isdigit()]))
                racetime = response.xpath("//span[@class='navRace']/span/text()").extract()[0]
                l.add_value('racetime', racetime)
                l.add_value('racecourse', response.xpath("//span[contains(@class,'placeRace')]/text()").extract()[0].strip())

                racename = response.xpath("//div[@class='info']/p/strong/strong[contains(@class,'uppercase')]/text()").extract()
                l.add_value("racename", racename)
                l.add_value('pm1', response.xpath("//ul[@class='results clearfix']/li/strong/text()").extract()[0].encode('ascii', 'ignore'))
                
                #race details
                rd = response.xpath("//ul[@class='results clearfix']")
                runners = rd.xpath("li[text()[contains(.,'Runners:')]]/strong/text()").extract()[0].strip()
                l.add_value("runners", runners)
                imperialdistance = rd.xpath("li[text()[contains(.,'Distance:')]]/strong/text()").extract()[0].strip()
                l.add_value("imperialdistance", imperialdistance)
                going = rd.xpath("li[text()[contains(.,'Going:')]]/strong/text()").extract()[0].strip()
                l.add_value("going", going)
                
                #race conds

                rc = response.xpath("//p[contains(@id,'raceConditionsText')]")
                l.add_value("raceconditions", rc.xpath("/text()"))
                totalpm = re.search('^.+(?= guaranteed)', rc.extract()[0])
                if totalpm is not None:
                    l.add_value("totalpm", totalpm.group(0))
                l.add_value("pmcurr", 'GBP')
                l.add_value("pm2", rc.xpath("b[text()[contains(.,'2nd')]]/following-sibling::text()").extract() )
                l.add_value("pm3", rc.xpath("b[text()[contains(.,'3rd')]]/following-sibling::text()").extract() )
                l.add_value("pm4", rc.xpath("b[text()[contains(.,'4th')]]/following-sibling::text()").extract() )
                l.add_value("pm5", rc.xpath("b[text()[contains(.,'5th')]]/following-sibling::text()").extract() )

                # TABLE OF RUNNERS
                rows = response.xpath("//table[@id='sc_horseCard']/tbody[contains(@id, 'sc_')]")
                for row in rows:
                    # cr class
                    l.add_value("horsenumber",row.select("tr[contains(@class,'cr')]/td[@class='t']/strong/text()").extract())
                    l.add_value("draw",row.select("tr[contains(@class,'cr')]/td[@class='t']/sup/text()").extract())
                    l.add_value("horsename",row.select("tr[contains(@class,'cr')]/td[3]/a/b/text()").extract())
                    horseurl = row.select("tr[contains(@class,'cr')]/td[3]/a/@href").extract()
                    l.add_value("rphorseid",horseurl[0].replace("&popup=1", "").split("=")[-1])

                    l.add_value("hage",row.select("tr[contains(@class,'cr')]/td[4]/text()").extract())
                    l.add_value("weight",row.select("tr[contains(@class,'cr')]/td[5]/div[1]/text()").extract())
                    l.add_value("OR",row.select("tr[contains(@class,'cr')]/td[5]/div[2]/text()").extract())
                    l.add_value("jockeyname",row.select("tr[contains(@class,'cr')]/td[6]/div[1]/a/text()").extract())
                    l.add_value("trainername",row.select("tr[contains(@class,'cr')]/td[6]/div[2]/a/text()").extract())
                    #2nd line
                    l.add_value("diomed",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='diomed']/text()").extract())
                    l.add_value("spotlight",row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='spotlight']/text()").extract())
                    l.add_value("owner", row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='owners']/a/text()").extract())
                    ownerurl = row.select("tr/td[contains(@class,'cardItemInfo')]/p[@class='owners']/a/@href").extract()
                    l.add_value("rpownerid", ownerurl[0].replace("&popup=1", "").split("=")[-1])

                        #previous form
                    lastrace = row.select("tr/td[contains(@class,'cardItemInfo')]/div[contains(@class,'forms')]")
                    if "There are no past perfomances on the Racing Post database for this horse" not in lastrace.select("text()").extract(): 
                        L1date = lastrace.select("table/tr[2]/td[2]/a/text()")
                        if L1date:
                            l.add_value("L1date", datetime.strptime(L1date.extract()[0], '%d%b%y'))
                            L1distgoing = lastrace.select("table/tr[2]/td[3]/b/a/following-sibling::text()[1]").extract()[0]
                            L1racetype = lastrace.select("table/tr[2]/td[3]/b/following-sibling::text()[1]").extract()[0]
                        ###need to work on these two
                            l.add_value("L1distance", getdistance(L1distgoing))
                            l.add_value("L1goingcode", ''.join( ''.join([ i for i in L1distgoing if not i.isdigit() ])   ).replace(".", "") )
                            l.add_value("L1racetype",L1racetype)

                            L1carriedwt = lastrace.select("table/tr[2]/td[4]/text()").extract()[0]
                            l.add_value("L1carriedwt",L1carriedwt)
                            L1comment = lastrace.select("table/tr[2]/td[5]/a/@title").extract()[0]
                            l.add_value("L1comment", L1comment)
                            L1pos = lastrace.select("table/tr[2]/td[5]/b[@class='black']/text()").extract()[0]
                            l.add_value("L1pos", L1pos)
                            L1SP = lastrace.select("table/tr[2]/td[5]/a/following-sibling::text()[1]").extract()[0]
                            l.add_value("L1SP", L1SP)
                            L1runners = lastrace.select("table/tr[2]/td[5]/b/following-sibling::text()[1]").extract()[0].replace('/', "")
                            l.add_value("L1runners", L1runners)
                        # L1ranon = datetime.strptime(lastrace.select("td[2]/a/text()").extract()[0], '%d%b%y')
                        # l.add_value("L1ranon",L1ranon)
                    # [u'<div class="forms">\n <p>There are no past perfomances on the Racing Post database for this horse</p></div>']
                    # L1ranon = datetime.strptime(lastrace.select("td[2]/a/text()").extract()[0], '%d%b%y')
                    # L1carriedwt = lastrace.select("td[4]/text()").extract()[0]
                    # L1pos = lastrace.select("td[5]/b[@class='black']/text()").extract()[0]
                    # L1comment = lastrace.select("td[5]/a/@title").extract()[0]

                    # l.add_value("L1ranon",L1ranon)
                    # l.add_value("L1carriedwt",L1carriedwt)
                    # l.add_value("L1pos", L1pos)
                    # l.add_value("L1comment", L1comment)
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

            # TABLE sc_horseCard
            #horsenumber
            #horsename
    
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

                yield l.load_item()

                

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
            l.add_value('racecourse', response.xpath('//title').extract()[0].split('|')[0].strip().split("At ")[-1])
            l.add_value('racetime', response.xpath('//title/text()').extract()[0].split('|')[0].strip().split(" Race")[0].replace("Results From The ", ""))
            # l.add_value('racename', response.xpath("//h3[@class='clearfix']/text()").extract()[0].strip())
            #race number?
            #race name, racetype

            racedetails = response.xpath("//div[@class='leftColBig']/ul/li/text()")
            l.add_value("raceclass", racedetails.extract()[0].split('\n')[1].replace("(", '').replace(")", "").strip())
            l.add_value("ratingband", racedetails.extract()[0].split('\n')[2].split(",")[0].replace("(", "").replace(")", "").strip())
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
            l.add_value('totalpm', sum(pms))

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
            #     sp
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