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

    name = "t23m_noise"

    url_prefix = 'https://t23m-navi.jp'

    ua = UserAgent()

    user_agent = ua.random

    allowed_domains = ["t23m-navi.jp"]

    start_urls = (
        url_prefix + '/members/login',
    )

    login_email    = 'wrzhao1987@yahoo.co.jp'
    login_password = 'wangyaya1123'

    collection = MongoClient(settings['MONGO_URI'])[settings['MONGO_DATABASE']].t23_room

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
            yield Request(url = self.list_page)

    def after_login(self, response):
        for mansion in self.collection.find({'sale.price': {'$lt': 100000}}):
            self.user_agent = self.ua.random
            yield Request(url = self.generate_url(mansion["mansion_id"]), callback = self.parse_detail_page) 

    def parse_detail_page(self, response):
        # prog = re.compile('(\d+)')
        # mansion_id = prog.findall(response.url)

        # mansion_id        = mansion_id[1]
        # mansion_name      = response.xpath(u"//th[contains(text(),'名称')]/following-sibling::td/strong/text()").extract_first()
        # mansion_name_list = response.xpath("//div[@class='breadcrumb_bg']/div[@id='breadcrumbs']/ul/li[@class='last']/strong/a/span/text()").extract_first()
        # mansion_name_kana = response.xpath("//div[@id='contents_main']/div[@class='section'][1]/div[@class='post-title']/p[@class='kana']/text()").extract_first()
        # address = response.xpath(u"//th[contains(text(),'住所')]/following-sibling::td/strong/text()").extract_first()
        # #traffic = response.xpath(u"//th[contains(text(),'最寄り駅')]/following-sibling::td/strong/text()").extract()
        # trafficAll = response.xpath(u"//th[contains(text(),'最寄り駅')]/following-sibling::td/descendant::*/text()").extract()
        # station = response.xpath(u"//th[contains(text(),'最寄り駅')]/following-sibling::td/strong/strong/text()").extract()
        # manage  = response.xpath(u"//th[contains(text(),'管理会社')]/following-sibling::td/strong/text()").extract_first()
        # rights  = response.xpath(u"//th[contains(text(),'土地権利')]/following-sibling::td/strong/text()").extract_first()
        # usage   = response.xpath(u"//th[contains(text(),'用途地域')]/following-sibling::td/strong/text()").extract_first()
        # constr  = response.xpath(u"//th[contains(text(),'建物構造')]/following-sibling::td/strong/text()").extract_first()
        # builtYm = response.xpath(u"//th[contains(text(),'建築年月')]/following-sibling::td/strong/text()").extract_first()
        # floorU  = response.xpath(u"//th[contains(text(),'地上階数')]/following-sibling::td/strong/text()").extract_first()
        # floorB  = response.xpath(u"//th[contains(text(),'地下階数')]/following-sibling::td/strong/text()").extract_first()
        # houses  = response.xpath(u"//th[contains(text(),'総戸数')]/following-sibling::td/strong/text()").extract_first()
        # primary_school  = response.xpath(u"//th[contains(text(),'小学校区')]/following-sibling::td/strong/text()").extract_first()
        # middile_school  = response.xpath(u"//th[contains(text(),'中学校区')]/following-sibling::td/strong/text()").extract_first()
        # old_bunjyo      = response.xpath(u"//th[contains(text(),'旧分譲主')]/following-sibling::td/strong/text()").extract_first()
        # cons_company    = response.xpath(u"//th[contains(text(),'施工会社')]/following-sibling::td/strong/text()").extract_first()

        
        # #traffic = self.formatTrafficInfo(traffic, station)
        # #trafficStringRaw = trafficAll,
        # #trafficStringFormatted = self.parse_traffic_info(trafficAll)

        # if manage is None:
        #     manage = ''
        # if mansion_name_kana is None:
        #     mansion_name_kana = ''
        # if mansion_name_list is None:
        #     mansion_name_list = ''
        # if rights is None:
        #     rights = ''
        # if usage is None:
        #     usage = ''
        # if constr is None:
        #     constr = ''
        # if builtYm is None:
        #     builtYm = ''
        # if floorU is None:
        #     floorU = 0
        # if floorB is None:
        #     floorB = 0
        # if houses is None:
        #     houses = 0
        # if primary_school is None:
        #     primary_school = ''
        # if middile_school is None:
        #     middile_school = ''
        # if old_bunjyo is None:
        #     old_bunjyo = ''
        # if cons_company is None:
        #     cons_company = ''

        # mansion_item = T23MansionItem(
        #     mansion_id = mansion_id,
        #     name       = mansion_name,
        #     mansion_name_list = mansion_name_list,
        #     mansion_name_kana = mansion_name_kana,
        #     address    = address,
        #     manage     = manage,
        #     built_year = builtYm,
        #     rights     = rights,
        #     usage      = usage,
        #     #traffic    = traffic,
        #     trafficStringRaw = trafficAll,
        #     construct  = constr,
        #     floor_above = floorU,
        #     floor_below = floorB,
        #     houses      = houses,
        #     primary_school = primary_school,
        #     middile_school = middile_school,
        #     old_bunjyo     = old_bunjyo,
        #     cons_company   = cons_company,
        # )

        # yield mansion_item

        sale_example = "//div[@id='sale_list_detale']/table[@id='price_sale_example_table']/tbody/tr/td/text()"
        rental_example = "//div[@id='sale_list_detale']/table[@id='rent_sale_example_table']/tbody/tr/td/text()"

        sale = response.xpath(sale_example).extract()
        rental = response.xpath(rental_example).extract()

        if len(sale) > 0:
            sale = self.chunk(sale, 4)
            sale = self.filterSampleInfo(sale)
        else:
            sale = []

        #print sale

        if len(rental) > 0:
            rental = self.chunk(rental, 4)
            rental = self.filterSampleInfo(rental)
        else:
            rental = []

        #print rental

        room_item = T23RoomItem(
            mansion_id = mansion_id,
            sale = sale,
            rental = rental,
        )

        yield room_item

        # print mansion_name, address, traffic, manage, rights, usage, constr, builtYm, floorU, floorB, houses


    def chunk(self, raw_list, size):
        result = []
        chunk = []
        if len(raw_list) % size == 0:
            group = len(raw_list) / size
            for i in range(1, group + 1):
                chunk = raw_list[ size * (i-1) : size * i ]
                result.append(chunk)
        return result

    def filterSampleInfo(self, chunked_list):
        result = []
        for item in chunked_list:
            print item[3].replace(',', '')
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

    def formatTrafficInfo(self, traffic, station):
        ret = []
        for i in range(len(station)):
            try:
                ret.append({
                    "line": traffic[2 * i],
                    "station": station[i].replace(u'「', '').replace(u'」', ''),
                    "time": self.parseNumber(traffic[2 * i + 1])
                })
            except IndexError:
                return ret
        return ret

    def parseNumber(self, rawStr):
        ret = re.findall(r'(\d+)', rawStr)
        return ret[0]

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
        
