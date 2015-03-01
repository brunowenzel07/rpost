import scrapy
import re



class RpostSpider(scrapy.Spider):
    name = "rpost"
    allowed_domains = ["www.racingpost.com"]
    start_urls = [
        "http://www.racingpost.com/horses/result_home.sd?race_id=618500&r_date=2015-02-27&popup=yes#results_top_tabs=re_&results_bottom_tabs=ANALYSIS"
    ]

    def parse(self, response):
        # filename = response.url.split("/")[-2]
        # with open(filename, 'wb') as f:
        #     f.write(response.body)

        # Results From The 2.10 Race At Doncaster | 27 February 2015 | Racing Post</title>'
        title = response.xpath('//title').extract()

        d = response.url.split("_")
        racedate = ''.join([ i for i in r[-1] if i.isdigit()]) #yyyymmdd
        rpraceid = ''.join([ i for i in r[-2] if i.isdigit()])

        # response.xpath('//title').extract()[0].split('|')[0].strip()
        racecourse = response.xpath('//title').extract()[0].split('|')[0].strip().split("At ")[-1]
        racetime = response.xpath('//title/text()').extract()[0].split('|')[0].strip().split(" Race")[0].replace("Results From The ", "")

        #raceinfo
        race = response.xpath("//div[@class='leftColBig']").extract()
        racename = response.xpath("//div[@class='leftColBig']/h3/text()").extract()[1].strip()

        # [u'', u' (Class 4) ', u' (0-105, 4yo+) (2m110y)', u' ', u' 2m\xbdf Good 8 hdles ']
        response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')
        raceclass = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[1].replace("(", '').replace(")", "").strip()

        # u' (0-105, 4yo+) (2m110y)' ratingband agerestrictin (imperialdistance mfy)
        racedata = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2]
        ratingband = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(",")[0].replace("(", "")
        agerestriction = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(")")[0].split(",")[-1].strip()
        imperialdistance = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[0].split('\n')[2].split(" ")[-1].replace("(", "").replace(")", "")

        pm = response.xpath("//div[@class='leftColBig']/ul/li/text()").extract()[1].split('\n')
        pms = []
        for _ in s.split():
            pms.append(_.decode('unicode_escape').encode('ascii', 'ignore'))
        #pms has prize money w , thousands ad . decimals no currency MONEY
