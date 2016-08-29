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

    name = "traffic"

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
        for mansion in self.collection.find({"trafficStringRaw": {"$eq": None}}):
            self.user_agent = self.ua.random
            yield Request(url = self.generate_url(mansion['mansion_id']), callback = self.parse_detail_page)

    def parse_detail_page(self, response):
        prog = re.compile('(\d+)')
        mansion_id = prog.findall(response.url)
        mansion_id = mansion_id[1]
        
        trafficAll = response.xpath(u"//th[contains(text(),'最寄り駅')]/following-sibling::td/descendant::*/text()").extract()
        for x in trafficAll:
            print x
        self.collection.update_one(
            {"mansion_id": mansion_id}, 
            {
                "$set": {
                    "trafficStringRaw": trafficAll,
                    "trafficStringFormatted": self.parse_traffic_info(trafficAll)
                }
            }
        )

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
        
