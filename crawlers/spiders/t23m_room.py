# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request, Response, TextResponse
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.response import open_in_browser
from scrapy.conf import settings
import requests, json, re
from crawlers.items import T23MansionItem, T23RoomItem
from pymongo import MongoClient
from fake_useragent import UserAgent

class T23mSpider(CrawlSpider):

    name = "t23_room"

    url_prefix = 'https://t23m-navi.jp'

    ua = UserAgent()

    user_agent = ua.random

    allowed_domains = ["t23m-navi.jp"]

    start_urls = (
        url_prefix + '/members/login',
    )

    login_email    = 'wrzhao1987@yahoo.co.jp'
    login_password = 'wangyaya1123'

    collection = MongoClient(settings['MONGO_URI'])[settings['MONGO_DATABASE']].t23_mansion

    rules = (
        Rule(LxmlLinkExtractor(
            allow=(r'\/list\/.*?',),
            restrict_xpaths=(
                "//div[@id='topMainimg01']/div[@class='topAreaList01']/ul/li/a",
                "//div[@id='sub']/nav[@id='lNavi']/ul/li[@class='first']/ul/li/a",
                "//div[@id='sub']/nav[@id='lNavi']/ul/li[@class='first']/a",
                "//div[@id='contents']/article[@id='main']/section/ul[@class='paging']/li/a")
            )
        ),
        Rule(LxmlLinkExtractor(allow=(r'\/indexes\/d\/\d+')), callback='parse_detail_page'),
    )

    def generate_url(self, mansion_id):
        return self.url_prefix + '/indexes/d/' + mansion_id
        pass

    def parse_start_url(self, response):
        try:
            login_action = scrapy.FormRequest.from_response(
                response,
                formdata  = {'data[Member][mail]': self.login_email, 'data[Member][password]': self.login_password},
                formxpath = "//div[@class='section'][1]/form",
                callback  = self.after_login,
                clickdata = {'type': 'image', 'name': 'mail'}
            )
            yield login_action
        except ValueError:
            pass
        

    def after_login(self, response):
        for mansion in self.collection.find({}):
            self.user_agent = self.ua.random
            yield Request(url = self.generate_url(mansion['mansion_id']), callback = self.parse_detail_page)

    def parse_detail_page(self, response):
        prog = re.compile('(\d+)')
        mansion_id = prog.findall(response.url)
        mansion_id = mansion_id[1]
        
        sale_example = "//div[@id='sale_list_detale']/table[@id='price_sale_example_table']/tbody/tr/td/text()"
        rental_example = "//div[@id='sale_list_detale']/table[@id='rent_sale_example_table']/tbody/tr/td/text()"

        sale = response.xpath(sale_example).extract()
        rental = response.xpath(rental_example).extract()

        if len(sale) > 0:
            sale = self.chunk(sale, 4)
            sale = self.filter_sample_info(sale)
        else:
            sale = []

        #print sale

        if len(rental) > 0:
            rental = self.chunk(rental, 4)
            rental = self.filter_sample_info(rental)
        else:
            rental = []

        #print rental

        room_item = T23RoomItem(
            mansion_id = mansion_id,
            sale = sale,
            rental = rental,
        )

        yield room_item

    def parse_traffic_info(self, traffic_raw_data):
        result = []
        for key in range(len(traffic_raw_data)):
            #traffic_raw_data[key] = traffic_raw_data[key].replace(u'「', '').replace(u'」', '')
            if re.search(ur'バス停徒歩\d+分 バス\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 4 : key + 1])
            elif re.search(ur'バス停徒歩\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 4 : key + 1])
            elif re.search(ur'徒歩\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 2 : key + 1])
        return result

    def chunk(self, raw_list, size):
        result = []
        chunk = []
        if len(raw_list) % size == 0:
            group = len(raw_list) / size
            for i in range(1, group + 1):
                chunk = raw_list[ size * (i-1) : size * i ]
                result.append(chunk)
        return result

    def filter_sample_info(self, chunked_list):
        result = []
        for item in chunked_list:
            info = {}

            date_digits = re.findall(r'\d+', item[0])
            info["date"]  = ''.join(date_digits)

            area_digits = re.findall(r'\d+', item[2])
            info["area"]  = int(area_digits[0])

            price_digits = re.findall(r'\d+', item[3].replace(',', ''))
            if len(price_digits) == 1:
                info['price'] = int(price_digits[0]) * 10000
            elif len(price_digits) == 2:
                info['price'] = int(price_digits[0]) * 100000000 + int(price_digits[1]) * 10000
            result.append(info)
        return result

    def parseNumber(self, rawStr):
        ret = re.findall(r'(\d+)', rawStr)
        return ret[0]

    def parse_traffic_info(self, traffic_raw_data):
        result = []
        if len(traffic_raw_data) == 2:
            result.append(traffic_raw_data)
            return result
        for key in range(len(traffic_raw_data)):
            #traffic_raw_data[key] = traffic_raw_data[key].replace(u'「', '').replace(u'」', '')
            if re.search(ur'バス停徒歩\d+分 バス\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 4 : key + 1])
            elif re.search(ur'バス停徒歩\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 4 : key + 1])
            elif re.search(ur'徒歩\d+分$', traffic_raw_data[key]):
                result.append(traffic_raw_data[key - 2 : key + 1])
        return result
        
