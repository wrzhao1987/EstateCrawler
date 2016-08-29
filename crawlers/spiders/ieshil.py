# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request, Response, TextResponse
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.response import open_in_browser
from scrapy.conf import settings
import requests, json, re
from crawlers.items import IeshilMansionItem, IeshilRoomItem
from pymongo import MongoClient
from fake_useragent import UserAgent

class IeshilSpider(CrawlSpider):

    name = "ieshil"

    url_prefix = 'https://www.ieshil.com'

    start_urls = (
        url_prefix + '/members/login/',
    )

    urls_list_page = (
        url_prefix + '/guide/tokyo/cities/',
    )

    api_list = {
        'rental': url_prefix + '/buildings/%s/rental_rooms?floor_number=%s',
        'sale'  : url_prefix + '/buildings/%s/sale_rooms?floor_number=%s'
    }

    login_email = 'wrzhao1987@yahoo.co.jp'
    login_password = 'wangyaya'

    allowed_domains = ["ieshil.com"]

    rules = (
        Rule(LxmlLinkExtractor(allow=(r'\/cities\d+/buildings\/.*?')), follow=True),
        Rule(LxmlLinkExtractor(allow=(r'\/stations\d+/buildings\/.*?')), follow=True),
        Rule(LxmlLinkExtractor(allow=(r'\/buildings\/\d+\/')), callback='parse_detail_page'),
    )

    mongo_client = MongoClient(settings['MONGO_URI'])[settings['MONGO_DATABASE']]
    ua = UserAgent()

    def parse_start_url(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {'member_login[email]': self.login_email, 'member_login[password]': self.login_password},
            callback = self.after_login
    )

    def after_login(self, response):
        for url in self.urls_list_page:
            yield Request(url = url)

    def update_room(self, response):
        if response.status == 200:
            room_info = json.loads(response.body)
            room_info = room_info['rooms']
            api_type = response.meta['type']
            mansion_id = response.meta['mansion_id']
            floor = int(response.meta['floor'])
            new_item = IeshilRoomItem(
                mansion_id = mansion_id,
                floor = floor,
            )
            new_item[api_type] = room_info
            return new_item


    def parse_detail_page(self, response):
        prog = re.compile('(\d+)')
        mansion_id = prog.findall(response.url)
        mansion_id = mansion_id[0]
        floor_list = response.xpath("//select[@id='room_floor_number_list']/option/@value").extract()
        # save room list into mongo
        for api_type, api_format in self.api_list.items():
            for floor in floor_list:
                yield Request(
                    url = api_format % (mansion_id, floor),
                    method = 'GET',
                    callback = self.update_room,
                    meta = {"type": api_type, "mansion_id": mansion_id, "floor": floor},
                    headers = {
                        'User-Agent': self.ua.random,
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                )
        mansion_name   = response.xpath("//tr[@class='table-vertical__row'][1]/td[@class='table-vertical__cell'][1]/span/span/text()").extract_first()
        address        = response.xpath("//tr[@class='table-vertical__row'][1]/td[@class='table-vertical__cell'][2]/span/text()").extract()
        manage_company = response.xpath("//tr[@class='table-vertical__row'][2]/td[@class='table-vertical__cell'][2]/text()").extract_first()
        built_year     = response.xpath("//li[@class='bldg-tags__item'][2]/div[@class='bldg-tags__of']/span/text()").re(r'\d+')
        floor_house    = response.xpath("//li[@class='bldg-tags__item'][3]/div[@class='bldg-tags__of']/span/text()").re(r'\d+')
        construct      = response.xpath("//li[@class='bldg-tags__item'][4]/div[@class='bldg-tags__of']/span/text()").extract_first()
        park           = response.xpath("//tr[@class='table-vertical__row'][3]/td[@class='table-vertical__cell'][1]/text()").extract_first()
        traffic        = response.xpath("//tr[@class='table-vertical__row'][3]/td[@class='table-vertical__cell'][2]/text()").extract()
        price          = response.xpath("//tr[@class='table-vertical__row'][2]/td[@class='table-vertical__cell'][1]/text()").extract_first()

        public_infra  = response.xpath("//div[@class='grid grid--col3 grid--mb15 mod-facility-list__group']/ul[@class='grid__inner']/li[@class='grid__item fac-list__item']/span[@class='fac-list__tx']/text()").extract()
        private_infra = response.xpath("//div[@class='grid grid--col3 grid--mb20 mod-facility-list__group']/ul[@class='grid__inner']/li[@class='grid__item fac-list__item']/span[@class='fac-list__tx']/text()").extract()

        try:
            street = address[2]
        except IndexError:
            street = ''

        try:
            built_year = built_year[0]
        except IndexError:
            built_year = 0

        try:
            houses = int(floor_house[1])
        except IndexError:
            houses = 0

        mansion_info = IeshilMansionItem(
            mansion_id = mansion_id,
            name       = mansion_name,
            prefecture = address[0],
            city       = address[1],
            street     = street,
            manage     = manage_company,
            built_year = built_year,
            floors     = int(floor_house[0]),
            houses     = houses,
            pub_infra  = public_infra,
            pri_infra  = private_infra,
            construct  = construct,
            traffic    = traffic,
            park       = park,
            price      = price,
        )

        yield mansion_info