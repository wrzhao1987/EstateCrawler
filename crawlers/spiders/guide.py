# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request, Response
from scrapy.utils.response import open_in_browser
import re
from crawlers.items import GuideItem1, GuideItem2, GuideItem3, GuideItem4, GuideItem5, GuideItem6, GuideItem7

class GuideSpider(CrawlSpider):
    name = "guide"
    allowed_domains = ["seikatsu-guide.com"]
    start_urls = (
        'http://www.seikatsu-guide.com/gov_info/main',
    )

    rules = (
        Rule(
            LxmlLinkExtractor(allow = (r'\/gov_info\/\?pid=.*')),
            follow = True
        ),
        Rule(
            LxmlLinkExtractor(allow = (r'\/citysearch\/\?ccd=.*?')),
            callback = 'parse_detail_page',
            follow = True
        ),
    )

    # def parse_start_url(self, response):
    #     pass

    def parse_detail_page(self, response):
        cid = self.get_cid(response.url)
        page_type = self.get_page_type(response.url)
        if (page_type is not None):
            item = getattr(self, 'parse_type_%s' % page_type)(response)
            if item:
                item['cid'] = cid
                return item

    def get_page_type(self, url):
        numbers = re.findall(r'(\d+)', url)
        if len(numbers) == 2:
            return str(numbers[1])

    def get_cid(self, url):
        numbers = re.findall(r'(\d+)', url)
        return str(numbers[0])


    def parse_type_1(self, response):
        '''
        基本：都道府県、都市
        国勢調査：総人口、増減率１、増減率２、人口男、人口女、世代数、昼間人口
        住民基本台帳：人口、年少人口率、生産年齢人口率、高齢人口率、転入者数、転入率、転出者数、転出率、外国人人口数、出生数、出生率、死亡数、死亡率、婚姻件数、婚姻率、離婚件数、離婚率
        行財政：歳入額、歳出額、地方税、将来負担比率、経常収支比率、職員数  
        '''
        city  = response.xpath("//div[@class='city_summary_in']/h3/a[2]/text()").extract_first()

        return GuideItem1(
            prefecture = response.xpath("//div[@class='city_summary_in']/h3/a[1]/text()").extract_first(),
            city = re.sub(r'\(.*\)', '', city),
            kokusei = {
                "population" :        self.parse_int(response.xpath(u"//td[contains(text(), '総人口')]/following-sibling::td[1]/text()").extract_first()),
                "change_rate_1" :     self.parse_percent(response.xpath(u"//td[contains(text(), '人口増減率（2005年／2010年）')]/following-sibling::td[1]/text()").extract_first()),
                "change_rate_2" :     self.parse_percent(response.xpath(u"//td[contains(text(), '人口増減率（2000年／2005年）')]/following-sibling::td[1]/text()").extract_first()),
                "population_male" :   self.parse_int(response.xpath(u"//td[contains(text(), '人口（男）')]/following-sibling::td[1]/text()").extract_first()),
                "population_female" : self.parse_int(response.xpath(u"//td[contains(text(), '人口（女）')]/following-sibling::td[1]/text()").extract_first()),
                "m_f_ratio":          self.parse_percent(response.xpath(u"//td[contains(text(), '人口性比（男／女）')]/following-sibling::td[1]/text()").extract_first()),
                "family" :            self.parse_int(response.xpath(u"//td[contains(text(), '世帯数')]/following-sibling::td[1]/text()").extract_first()),
                "daily_pop" :         self.parse_int(response.xpath(u"//td[contains(text(), '昼間人口')]/following-sibling::td[1]/text()").extract_first()),
            },
            daicho = {
                "population":  self.parse_int(response.xpath(u"//td[contains(text(), '人口総数')]/following-sibling::td[1]/text()").extract_first()),
                "young_rate":  self.parse_percent(response.xpath(u"//td[contains(text(), '年少人口率（15歳未満）')]/following-sibling::td[1]/text()").extract_first()),
                "middle_rate": self.parse_percent(response.xpath(u"//td[contains(text(), '生産年齢人口率（15～64歳）')]/following-sibling::td[1]/text()").extract_first()),
                "old_rate":    self.parse_percent(response.xpath(u"//td[contains(text(), '高齢人口率（65歳以上）')]/following-sibling::td[1]/text()").extract_first()),
                "change_average": self.parse_float(response.xpath(u"//td[contains(text(), '人口1000人当たりの人口増減数')]/following-sibling::td[1]/text()").extract_first()),
                "enter_num":   self.parse_int(response.xpath(u"//td[contains(text(), '転入者数')]/following-sibling::td[1]/text()").extract_first()),
                "enter_rate":  self.parse_float(response.xpath(u"//td[contains(text(), '転入者数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "exit_num":    self.parse_int(response.xpath(u"//td[contains(text(), '転出者数')]/following-sibling::td[1]/text()").extract_first()),
                "exit_rate":   self.parse_float(response.xpath(u"//td[contains(text(), '転出者数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "foregin":     self.parse_int(response.xpath(u"//td[contains(text(), '外国人人口数')]/following-sibling::td[1]/text()").extract_first()),
                "birth_num":   self.parse_int(response.xpath(u"//td[contains(text(), '出生数')]/following-sibling::td[1]/text()").extract_first()),
                "birth_rate":  self.parse_float(response.xpath(u"//td[contains(text(), '出生数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "death_num":   self.parse_int(response.xpath(u"//td[contains(text(), '死亡数')]/following-sibling::td[1]/text()").extract_first()),
                "death_rate":  self.parse_float(response.xpath(u"//td[contains(text(), '死亡数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "marry_num":   self.parse_int(response.xpath(u"//td[contains(text(), '婚姻件数')]/following-sibling::td[1]/text()").extract_first()),
                "marry_rate":  self.parse_float(response.xpath(u"//td[contains(text(), '婚姻件数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "break_num":   self.parse_int(response.xpath(u"//td[contains(text(), '離婚件数')]/following-sibling::td[1]/text()").extract_first()),
                "break_rate":  self.parse_float(response.xpath(u"//td[contains(text(), '離婚件数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
            },
            area = {
                "total":   self.parse_float(response.xpath(u"//td[contains(text(), '総面積')]/following-sibling::td[1]/text()").extract_first()),
                "usable":  self.parse_float(response.xpath(u"//td[contains(text(), '可住地面積')]/following-sibling::td[1]/text()").extract_first()),
                "density": self.parse_int(response.xpath(u"//td[contains(text(), '可住地人口密度')]/following-sibling::td[1]/text()").extract_first()),
            },
            gov = {
                "income":              self.parse_int(response.xpath(u"//td[contains(text(), '歳入額')]/following-sibling::td[1]/text()").extract_first(), 1000),
                "income_average":      self.parse_int(response.xpath(u"//td[contains(text(), '歳入額')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first(), 1000),
                "cost":                self.parse_int(response.xpath(u"//td[contains(text(), '歳出額')]/following-sibling::td[1]/text()").extract_first(), 1000),
                "cost_average":        self.parse_int(response.xpath(u"//td[contains(text(), '歳出額')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first(), 1000),
                "tax":                 self.parse_int(response.xpath(u"//td[contains(text(), '地方税')]/following-sibling::td[1]/text()").extract_first(), 1000),
                "tax_average":         self.parse_int(response.xpath(u"//td[contains(text(), '地方税')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first(), 1000),
                "finance_index":       self.parse_float(response.xpath(u"//td[contains(text(), '財政力指数')]/following-sibling::td[1]/text()").extract_first()),
                "public_cost_average": self.parse_int(response.xpath(u"//td[contains(text(), '人口１人当りの公共事業費')]/following-sibling::td[1]/text()").extract_first(), 1000),
                "burden_rate":         self.parse_percent(response.xpath(u"//td[contains(text(), '将来負担比率')]/following-sibling::td[1]/text()").extract_first()),
                "usual_io_rate":       self.parse_percent(response.xpath(u"//td[contains(text(), '経常収支比率')]/following-sibling::td[1]/text()").extract_first()),
                "worker_num":          self.parse_int(response.xpath(u"//td[contains(text(), '市区職員総数')]/following-sibling::td[1]/text()").extract_first()),
                "worker_rate":         self.parse_float(response.xpath(u"//td[contains(text(), '市区職員総数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
            },
        )

    def parse_type_2(self, response):
        '''
        気候：年間平均気温、年間降水量、年間日照時間   
        '''
        return GuideItem2(
            weather = {
                "temp_average":  self.parse_float(response.xpath(u"//td[contains(text(), '年間平均気温')]/following-sibling::td[1]/text()").extract_first()),
                "rain_amount":   self.parse_float(response.xpath(u"//td[contains(text(), '年間降水量')]/following-sibling::td[1]/text()").extract_first()),
                "sunshine_hour": self.parse_float(response.xpath(u"//td[contains(text(), '年間日照時間')]/following-sibling::td[1]/text()").extract_first()),
            }
        )

    def parse_type_3(self, response):
        '''
        公共料金：ガス料金、水道料金、下水道料金
        安心、安全：建物火災出火件数、人口1万人当たり、刑法犯認知件数、人口千人当たり
        居住・文化：公民館数、郵便局数、百貨店・総合スーバー数、都市公園数、公園総面積、一人当たりの公園面積、図書館数、蔵書数、人口一人当たり、音声・映像資料など数    
        '''
        return GuideItem3(
            public  = {
                "gas":     self.parse_int(response.xpath(u"//td[contains(text(), 'ガス料金')]/following-sibling::td[2]/text()").extract_first()),
                "suido":   self.parse_int(response.xpath(u"//td[contains(text(), '水道料金')]/following-sibling::td[2]/text()").extract_first()),
                "gesuido": self.parse_int(response.xpath(u"//td[contains(text(), '下水道料金')]/following-sibling::td[2]/text()").extract_first()),
            },
            safety  = {
                "fire":          self.parse_int(response.xpath(u"//td[contains(text(), '建物火災出火件数')]/following-sibling::td[1]/text()").extract_first()),
                "fire_average":  self.parse_float(response.xpath(u"//td[contains(text(), '建物火災出火件数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "crime":         self.parse_int(response.xpath(u"//td[contains(text(), '刑法犯認知件数')]/following-sibling::td[1]/text()").extract_first()),
                "crime_average": self.parse_float(response.xpath(u"//td[contains(text(), '刑法犯認知件数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
            },
            culture = {
                "komin":                self.parse_int(response.xpath(u"//td[contains(text(), '公民館数')]/following-sibling::td[1]/text()").extract_first()),
                "post":                 self.parse_int(response.xpath(u"//td[contains(text(), '郵便局数')]/following-sibling::td[1]/text()").extract_first()),
                "depart":               self.parse_int(response.xpath(u"//td[contains(text(), '百貨店・総合スーパー数')]/following-sibling::td[1]/text()").extract_first()),
                "park":                 self.parse_int(response.xpath(u"//td[contains(text(), '都市公園数')]/following-sibling::td[1]/text()").extract_first()),
                "park_area":            self.parse_int(response.xpath(u"//td[contains(text(), '都市公園総面積')]/following-sibling::td[1]/text()").extract_first()),
                "park_area_average":    self.parse_float(response.xpath(u"//td[contains(text(), '1人当たりの都市公園面積')]/following-sibling::td[1]/text()").extract_first()),
                "library":              self.parse_int(response.xpath(u"//td[contains(text(), '図書館数')]/following-sibling::td[1]/text()").extract_first()),
                "library_book":         self.parse_int(response.xpath(u"//td[contains(text(), '蔵書数')]/following-sibling::td[1]/text()").extract_first()),
                "library_book_average": self.parse_float(response.xpath(u"//td[contains(text(), '蔵書数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "library_media":        self.parse_int(response.xpath(u"//td[contains(text(), '音声・映像資料等数')]/following-sibling::td[1]/text()").extract_first()),
            },
        )

    def parse_type_4(self, response):
        '''
        育児：チャイルドシート支援制度、乳幼児・子ども医療費助成＜通院＞：対象年齢、自己負担、所得制限、 乳幼児・子ども医療費助成＜入院＞：対象年齢、自己負担、所得制限、
        公立保育所、ゼロから保育、定員
        私立保育所、ゼロから保育、定員
        待機児童数
        '''
        return GuideItem4(
            support = {
                "child_sheet":             self.parse_yes_no(response.xpath(u"//p[contains(text(), 'チャイルドシート支援制度')]/parent::td/following-sibling::td/text()").extract_first()),
                "tsuin_age":               self.parse_text(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<通院>')]/following-sibling::table/tr[1]/td[2]/text()").extract_first()),
                "tsuin_burden":            self.parse_yes_no(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<通院>')]/following-sibling::table/tr[2]/td[2]/text()").extract_first()),
                "tsuin_income_limit":      self.parse_yes_no(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<通院>')]/following-sibling::table/tr[3]/td[2]/text()").extract_first()),
                "nyuin_age":               self.parse_text(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<入院>')]/following-sibling::table/tr[1]/td[2]/text()").extract_first()),
                "nyuin_burden":            self.parse_yes_no(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<入院>')]/following-sibling::table/tr[2]/td[2]/text()").extract_first()),
                "nyuin_income_limit":      self.parse_yes_no(response.xpath(u"//p[contains(text(), '乳幼児・子ども医療費助成<入院>')]/following-sibling::table/tr[3]/td[2]/text()").extract_first()),
            },
            nurture = {
                "public_count":            self.parse_int(response.xpath(u"//p[contains(text(), '公立保育所')]/following-sibling::table/tr/td[contains(text(), '保育所数')]/following-sibling::td[1]/text()").extract_first()),
                "public_count_from_zero":  self.parse_int(response.xpath(u"//p[contains(text(), '公立保育所')]/following-sibling::table/tr/td[contains(text(), '0歳児保育を実施している保育所')]/following-sibling::td[1]/text()").extract_first()),
                "public_booked":           self.parse_int(response.xpath(u"//p[contains(text(), '公立保育所')]/following-sibling::table/tr/td[contains(text(), '在籍児童数')]/following-sibling::td[1]/text()").extract_first()),
                "public_limit":            self.parse_int(response.xpath(u"//p[contains(text(), '公立保育所')]/following-sibling::table/tr/td[contains(text(), '定員数')]/following-sibling::td[1]/text()").extract_first()),
                "private_count":           self.parse_int(response.xpath(u"//p[contains(text(), '私立保育所')]/following-sibling::table/tr/td[contains(text(), '保育所数')]/following-sibling::td[1]/text()").extract_first()),
                "private_count_from_zero": self.parse_int(response.xpath(u"//p[contains(text(), '私立保育所')]/following-sibling::table/tr/td[contains(text(), '0歳児保育を実施している保育所')]/following-sibling::td[1]/text()").extract_first()),
                "private_booked":          self.parse_int(response.xpath(u"//p[contains(text(), '私立保育所')]/following-sibling::table/tr/td[contains(text(), '在籍児童数')]/following-sibling::td[1]/text()").extract_first()),
                "private_limit":           self.parse_int(response.xpath(u"//p[contains(text(), '私立保育所')]/following-sibling::table/tr/td[contains(text(), '定員数')]/following-sibling::td[1]/text()").extract_first()),
                "waiting":                 self.parse_int(response.xpath(u"//p[contains(text(), '保育所入所待機児童数')]/parent::td/following-sibling::td[1]/text()").extract_first())
            },
        )
    def parse_type_5(self, response):

        return GuideItem5(
            edu_kinder = {
                "public_count":   self.parse_int(response.xpath(u"//td[contains(text(), '公立幼稚園数(国立を含む)')]/following-sibling::td[1]/text()").extract_first()),
                "private_count":  self.parse_int(response.xpath(u"//td[contains(text(), '私立幼稚園数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count":     self.parse_int(response.xpath(u"//td[contains(text(), '園児数')]/following-sibling::td[1]/text()").extract_first()),
                "has_public":     self.parse_yes_no(response.xpath(u"//td[contains(text(), '公立幼稚園の有無')]/following-sibling::td[1]/text()").extract_first()),
                "pub_discount":   self.parse_yes_no(response.xpath(u"//td[contains(text(), '公立幼稚園の入園料・保育料減免')]/following-sibling::td[1]/text()").extract_first()),
                "pri_enter_dsct": self.parse_yes_no(response.xpath(u"//p[contains(text(), '私立幼稚園補助金<入園料>')]/parent::td/following-sibling::td[1]/text()").extract_first()),
                "pri_care_dsct":  self.parse_yes_no(response.xpath(u"//p[contains(text(), '私立幼稚園補助金<保育料>')]/parent::td/following-sibling::td[1]/text()").extract_first()),
                "anti_quake":     self.parse_percent(response.xpath(u"//td[contains(text(), '公立幼稚園の耐震化率')]/parent::td/following-sibling::td[1]/text()").extract_first()),
            },
            edu_primary = {
                "count":              self.parse_int(response.xpath(u"//td[contains(text(), '小学校数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count":         self.parse_int(response.xpath(u"//td[contains(text(), '小学校児童数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count_average": self.parse_float(response.xpath(u"//td[contains(text(), '公立小学校1学級当たりの平均児童数')]/following-sibling::td[1]/text()").extract_first()),
                "selectable":         self.parse_text(response.xpath(u"//td[contains(text(), '公立小学校の学校選択制')]/following-sibling::td[1]/text()").extract_first()),
                "computer_average":   self.parse_float(response.xpath(u"//td[contains(text(), '教育用コンピュータ1台当たりの児童数')]/following-sibling::td[1]/text()").extract_first()),
                "fiber_rate":         self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　小学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '光ファイバー回線によるインターネット接続率')]/following-sibling::td[1]/text()").extract_first()),
                "30mbps_rate":        self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　小学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '30Mbps以上の回線によるインターネット接続率')]/following-sibling::td[1]/text()").extract_first()),
                "digital_book_rate":  self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　小学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), 'デジタル教科書の整備率')]/following-sibling::td[1]/text()").extract_first()),
                "digital_blackboard_rate": self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　小学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '電子黒板のある学校の割合')]/following-sibling::td[1]/text()").extract_first()),
            },
            edu_middle = {
                "count":              self.parse_int(response.xpath(u"//td[contains(text(), '中学校数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count":         self.parse_int(response.xpath(u"//td[contains(text(), '中学校生徒数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count_average": self.parse_float(response.xpath(u"//td[contains(text(), '公立中学校1学級当たりの平均生徒数')]/following-sibling::td[1]/text()").extract_first()),
                "selectable":         self.parse_text(response.xpath(u"//td[contains(text(), '公立中学校の学校選択制')]/following-sibling::td[1]/text()").extract_first()),
                "computer_average":   self.parse_float(response.xpath(u"//td[contains(text(), '教育用コンピュータ1台当たりの生徒数')]/following-sibling::td[1]/text()").extract_first()),
                "fiber_rate":         self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　中学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '光ファイバー回線によるインターネット接続率')]/following-sibling::td[1]/text()").extract_first()),
                "30mbps_rate":        self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　中学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '30Mbps以上の回線によるインターネット接続率')]/following-sibling::td[1]/text()").extract_first()),
                "digital_book_rate":  self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　中学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), 'デジタル教科書の整備率')]/following-sibling::td[1]/text()").extract_first()),
                "digital_blackboard_rate": self.parse_percent(response.xpath(u"//h4[contains(text(), '教育　中学校')]/parent::div/following-sibling::table[1]/tr/td[contains(text(), '電子黒板のある学校の割合')]/following-sibling::td[1]/text()").extract_first()),
            },
            edu_infra = {
                "anti_quake_rate": self.parse_percent(response.xpath(u"//td[contains(text(), '公立小中学校の耐震化率')]/following-sibling::td[1]/text()").extract_first()),
                "food":            self.parse_text(response.xpath(u"//td[contains(text(), '学校給食')]/following-sibling::td[1]/text()").extract_first()),
                "food_by_minkan":  self.parse_text(response.xpath(u"//td[contains(text(), '学校給食民間委託')]/following-sibling::td[1]/text()").extract_first()),
            },
            edu_senior = {
                "count":      self.parse_int(response.xpath(u"//td[contains(text(), '高等学校数')]/following-sibling::td[1]/text()").extract_first()),
                "kids_count": self.parse_int(response.xpath(u"//td[contains(text(), '高等学校生徒数')]/following-sibling::td[1]/text()").extract_first()),
            },
        )

    def parse_type_6(self, response):
        return GuideItem6(
            medical = {
                "hospital_count":            self.parse_int(response.xpath(u"//td[contains(text(), '一般病院総数')]/following-sibling::td[1]/text()").extract_first()),
                "sickbed_count":             self.parse_int(response.xpath(u"//td[contains(text(), '一般病床')]/following-sibling::td[1]/text()").extract_first()),
                "sickbed_average":           self.parse_float(response.xpath(u"//td[contains(text(), '一般病床')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "clinic_count":              self.parse_int(response.xpath(u"//td[contains(text(), '一般診療所総数')]/following-sibling::td[1]/text()").extract_first()),
                "dentistry_count":           self.parse_int(response.xpath(u"//td[contains(text(), '歯科診療所総数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_count":              self.parse_int(response.xpath(u"//td[contains(text(), '医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_average":            self.parse_float(response.xpath(u"//td[contains(text(), '医師数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "doctor_naika_count":        self.parse_int(response.xpath(u"//td[contains(text(), '内科医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_syonika_count":      self.parse_int(response.xpath(u"//td[contains(text(), '小児科医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_syonika_average":    self.parse_float(response.xpath(u"//td[contains(text(), '小児科医師数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "doctor_geka_count":         self.parse_int(response.xpath(u"//td[contains(text(), '外科医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_sanfujinka_count":   self.parse_int(response.xpath(u"//td[contains(text(), '産婦人科医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_sanfujinka_average": self.parse_float(response.xpath(u"//td[contains(text(), '産婦人科医師数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
                "doctor_shika_count":        self.parse_int(response.xpath(u"//td[contains(text(), '歯科医師総数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_syonishika_count":   self.parse_int(response.xpath(u"//td[contains(text(), '小児歯科医師数')]/following-sibling::td[1]/text()").extract_first()),
                "doctor_syonishika_average": self.parse_float(response.xpath(u"//td[contains(text(), '小児歯科医師数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
            },
            care = {
                "care_insurance":            self.parse_int(response.xpath(u"//td[contains(text(), '介護保険料基準額（月額）')]/following-sibling::td[1]/text()").extract_first()),
                "old_home":                  self.parse_int(response.xpath(u"//td[contains(text(), '老人ホーム定員数')]/following-sibling::td[1]/text()").extract_first()),
                "old_home_average":          self.parse_float(response.xpath(u"//td[contains(text(), '老人ホーム定員数')]/parent::tr/following-sibling::tr[1]/td[2]/text()").extract_first()),
            },
        )

    def parse_type_7(self, response):
        '''
        土地平均価格（住宅）、土地平均価格（商業）  
        '''
        return GuideItem7(
            land_price = {
                "housing"  : self.parse_int(response.xpath("//table[@class='data_table'][1]/tr[1]/td[2]/text()").extract_first()),
                "business" : self.parse_int(response.xpath("//table[@class='data_table'][1]/tr[@class='gray_tr']/td[2]/text()").extract_first())
            }
        )

    def parse_int(self, raw_str, base = 1):
        if raw_str is None or len(raw_str) == 0:
            return None
        number = re.findall(r'(\d+)', raw_str.replace(',', ''))
        if len(number):
            return int(number[0]) * base

    def parse_float(self, raw_str):
        if raw_str is None or len(raw_str) == 0:
            return None
        number = re.findall(r'(\d+\.?\d+)', raw_str.replace(',', ''))
        if len(number):
            return float(number[0])

    def parse_percent(self, raw_str):
        if raw_str is None or len(raw_str) == 0:
            return None
        number = re.findall(r'(\d+\.?\d+)', raw_str)
        if (len(number)):
            return float(number[0]) / 100

    def parse_yes_no(self, raw_str):
        if raw_str is None:
            return 0
        if re.search(ur'あり', raw_str):
            return 1
        elif re.search(ur'なし', raw_str):
            return 0

    def parse_text(self, raw_str):
        if not raw_str:
            return None
        return raw_str
