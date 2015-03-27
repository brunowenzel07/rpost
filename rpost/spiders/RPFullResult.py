# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request, FormRequest
from scrapy import log
import random
import re
from datetime import datetime
from rpost.items import RPostItemsLoader
import json

# URL of container for login page.
login_container_URL = u'http://www.racingpost.com/modal_dialog/container.sd?modal=false&modalType=login&layout=Home&protoSecure=0&from=header&senderUrl=%s&random=%d' % (u'http%3A//www.racingpost.com/', random.random()*10000000000000000)
# Profile URL.
profile_URL = u'https://reg.racingpost.com/cde/../account/profile.sd?_=%d' % (random.random()*10000000000000000)
# Full result main page.
fullResultMainURL = u'http://www.racingpost.com/horses2/results/home.sd?r_date=%s'

# Crawler for racingpost.com.
class RPFullResult(CrawlSpider):
    name = u'RPFullResult'
    allowed_domains = [u'www.racingpost.com', u'reg.racingpost.com']
    start_urls = [u'http://www.racingpost.com']
    rules = ()
    login = u''
    password = u''
    date = u''

    def __init__(self, login = u'', password = u'', result_date = u'', *args, **kwargs):
        super(RPFullResult, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.date = result_date
        if not self.date:
            self.date = datetime.date.today()
        self.fullResultMainURL = fullResultMainURL % (self.date)

    # Set login and password.
    def setUser(self, login, password):
        if not login or not password:
            return
        self.login = login
        self.password = password

    # Parse main page.
    def parse(self, response):
        if not response:
            log.msg(u'Error. Start page is empty.', logLevel = log.ERROR)
            return []
        return [Request(url = login_container_URL, callback = self.parse_login_container),]

    # Parse login container page.
    def parse_login_container(self, response):
        if not response:
            log.msg(u'Error. Login container page is empty.', logLevel = log.ERROR)
            return []
        # Get the login page URL.
        login_page_info = re.search(u'<iframe.+id=\"logInFrame\" .* src=\"(\S+)\".*\/>', response.body)
        if not login_page_info:
            log.msg(u'Error. Login info page is empty.', logLevel = log.ERROR)
            return []
        return [Request(url = login_page_info.group(1), callback = self.parse_login_page)]

    # Parse login page.
    def parse_login_page(self, response):
        if not response:
            log.msg(u'Error. Login page is empty.', logLevel = log.ERROR)
            return []
        if not self.login or not self.password:
            log.msg(u'Error. Empty user info.', logLevel = log.ERROR)
            return
        # Just get form for login from page and send request.
        return [FormRequest.from_response(response, formdata = {u'in_un': self.login, u'in_pw': self.password}, callback = self.logged_in)]

    # Handle login result.
    def logged_in(self, response):
        if not response:
            log.msg(u'Error. Logged in page is empty.', logLevel = log.ERROR)
            return []
        state_info = re.search(u'state=invalid', response.body)
        if state_info:
            log.msg(u'Authentication failed.', logLevel = log.ERROR)
            return []
        # Get profile page for checking if looged in.
        return [Request(url = profile_URL, callback = self.parse_profile_page),]

    # Parse profile page for checking if logged in.
    def parse_profile_page(self, response):
        if not response:
            log.msg(u'Error. Profile page is empty.', logLevel = log.ERROR)
            return []
        login_info = re.search(u'<h1>(.*)<\/h1>', response.body)
        if not login_info:
            log.msg(u'Authentication failed.', logLevel = log.ERROR)
            return []
        if login_info.group(1) != self.login:
            log.msg(u'Authentication failed.', logLevel = log.ERROR)
            return []
        return [Request(url = self.fullResultMainURL, callback = self.parse_full_result_main_page),]

    ## RACEDATE PAGE get full result pages, each is a race    
    def parse_full_result_main_page(self, response):
        if not response:
            log.msg(u'Error. Full result main page is empty.', logLevel = log.ERROR)
            return []
        links = re.findall(u'<a href="(\S+)" .*>Full result</a>', response.body)
        if not links:
            log.msg(u'No any links to races found.', logLevel = log.WARNING)
            return []
        reqs = []
        for link in links:
            link = u'http://%s%s' % (self.allowed_domains[0], link)
            reqs.append(Request(url = link, callback = self.parse_full_result_home))
        return reqs

    ##parse races
    def parse_full_result_home(self, response):
        if not response:
            log.msg(u'Error. Full result home page is empty.', logLevel = log.ERROR)
            return []
        # Getting data for tabs for extra data.
        analysis_URL =u''
        results_bottom_tabs_data = re.search(u'var results_bottom_tabs (.*)\s', response.body)
        if not results_bottom_tabs_data:
            log.msg(u'Error in getting extra data script.', logLevel = log.WARNING)
        else:
            jdata = None
            try:
                jdata = json.loads(results_bottom_tabs_data.group(0).split(u';')[1].split(u' = ')[1])
                analysis_local = jdata[u'ANALYSIS'][u'url']
                analysis_URL = u'http://%s%s' % (self.allowed_domains[0], analysis_local)
            except:
                log.msg(u'Error. Json data of extra data not found.')
                pass
        f = open(u'result', 'a+')
        f.write(response.body)
        if analysis_URL:
            return [Request(url = analysis_URL, callback = self.parse_analysis_page)]
        return []

    # ANALYSIS extra data.
    def parse_analysis_page(self, response):
        if not response:
            log.msg(u'Error. Full analysis page is empty.', logLevel = log.ERROR)
            return []
        f = open(u'analysis', 'a+')
        f.write(response.body)
