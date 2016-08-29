# -*- coding: utf-8 -*-
import scrapy
import requests, json, re, urllib, copy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request, Response, TextResponse
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.conf import settings
#from fake_useragent import UserAgent
from crawlers.items import HomesMapMansionItem, HomesMapRoomItem

class HomesMapSpider(CrawlSpider):
    name = "homes-map"
    # download_delay = 1.0
    #ua = UserAgent()

    url_prefix = 'http://www.homes.co.jp/price-map/api/'

    box_config = {
        'tokyo'   : {"start": [35.1286277, 138.9427579], "end": [35.8986468, 139.944383]},
        'kanagawa': {"start": [35.1286277, 138.9157521], "end": [35.6727538, 139.8358472]},
        'chiba'   : {"start": [34.8991264, 139.739439],  "end": [36.1041115, 140.8812059]},
        'saitama' : {"start": [35.7535212, 138.7113353], "end": [36.2835566, 139.9000999]},
    }

    lat_offset = 0.022
    lng_offset = 0.040
    
    allowed_domains = ["homes.co.jp"]

    start_urls = (
        'http://www.homes.co.jp/',
    )

    api_mansion_format = url_prefix + 'buildings?geo_sw=%s&geo_ne=%s&geo_type=1&building_type=1&offset=%s'
    api_room_format    = url_prefix + 'dwelling_units?assessed_price=1&building_id=%s&offset=%s' 

    rules = (
        Rule(LxmlLinkExtractor(allow=(r'\/api\/buildings.*?')),      follow=False, callback='parse_mansions'),
        Rule(LxmlLinkExtractor(allow=(r'\/api\/dwelling_units.*?')), follow=False, callback='parse_rooms'),
    )

    def __init__(self, prefecture='', *args, **kwargs):
        super(HomesMapSpider, self).__init__(*args, **kwargs)

        if (not prefecture):
            prefecture = 'tokyo'
        self.start_lat = self.box_config[prefecture]["start"][0]
        self.start_lng = self.box_config[prefecture]["start"][1]
        self.end_lat   = self.box_config[prefecture]["end"][0]
        self.end_lng   = self.box_config[prefecture]["end"][1]


    def parse_start_url(self, response):
        lat = self.start_lat
        lng = self.start_lng
        for lat in self.frange(self.start_lat, self.end_lat, self.lat_offset):

            for lng in self.frange(self.start_lng, self.end_lng, self.lng_offset):

                yield self.generate_mansion_request(
                    [lat, lng],
                    [lat + self.lat_offset, lng + self.lng_offset],
                    0
                )

    def parse_mansions(self, response):
        json_payload = json.loads(response.body)
        pager = json_payload['result']['result_set']
        building_ids = []
        for item in json_payload['result']['row_set']:
            # self.print_mansion_detail(item)
            mansion_item = HomesMapMansionItem()
            for key, value in item.items():
                mansion_item[key] = value
            yield mansion_item
            building_ids.append(item['building_id'])

        if pager["last"] != pager["total_hits"]:
            yield self.generate_mansion_request(response.meta['geo_sw'], response.meta['geo_ne'], pager['last'])
        yield self.generate_room_request(building_ids, 0)

    def parse_rooms(self, response):
        json_payload = json.loads(response.body)
        pager = json_payload['result']['result_set']
        for item in json_payload['result']['row_set']:
            #self.print_room_detail(item)

            room_item = HomesMapRoomItem()
            for key, value in item.items():
                room_item[key] = value
            yield room_item
        if pager["last"] != pager["total_hits"]:
            yield self.generate_room_request(response.meta["building_ids"], pager["last"])


    def generate_mansion_request(self, geo_sw, geo_ne, offset):
        return Request(
            url = self.api_mansion_format % (self.my_encoded_array(geo_sw), self.my_encoded_array(geo_ne), offset),
            method = 'GET',
            meta = {'geo_sw': geo_sw, 'geo_ne': geo_ne},
            headers = {
                #'User-Agent': self.ua.random,
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'X-Requested-With': 'XMLHttpRequest',
            },
            callback = self.parse_mansions,
        )

    def generate_room_request(self, building_ids, offset):
        return Request(
            url = self.api_room_format % (self.my_encoded_array(building_ids), offset),
            method = 'GET',
            meta = {'building_ids': building_ids},
            headers = {
                #'User-Agent': self.ua.random,
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'X-Requested-With': 'XMLHttpRequest',
            },
            callback = self.parse_rooms,
        )

    def my_encoded_array(self, array_data):
        return urllib.quote(','.join(map(lambda n:str(n), array_data)))

    def print_mansion_detail(self, mansion_row):
        print mansion_row['building_name'], mansion_row['full_address'], mansion_row['lng'], mansion_row['lat'], mansion_row['floor_count']

    def print_room_detail(self, room_row):
        print room_row

    def frange(self, start, stop, step):
        i = start
        while i < stop:
            yield i
            i += step
