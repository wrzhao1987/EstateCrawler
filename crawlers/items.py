# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class IeshilMansionItem(scrapy.Item):
    mansion_id = scrapy.Field()
    name       = scrapy.Field()
    prefecture = scrapy.Field()
    city       = scrapy.Field()
    street     = scrapy.Field()
    manage     = scrapy.Field()
    built_year = scrapy.Field()
    floors     = scrapy.Field()
    houses     = scrapy.Field()
    pub_infra  = scrapy.Field()
    pri_infra  = scrapy.Field()
    construct  = scrapy.Field()
    traffic    = scrapy.Field()
    park       = scrapy.Field()
    price      = scrapy.Field()

class IeshilRoomItem(scrapy.Item):
    mansion_id = scrapy.Field()
    floor = scrapy.Field()
    rental = scrapy.Field()
    sale = scrapy.Field()

class T23MansionItem(scrapy.Item):
    url         = scrapy.Field()
    mansion_id  = scrapy.Field()
    name        = scrapy.Field()
    address     = scrapy.Field()
    manage      = scrapy.Field()
    built_year  = scrapy.Field()
    rights      = scrapy.Field()
    usage       = scrapy.Field()
    construct   = scrapy.Field()
    floor_above = scrapy.Field()
    floor_below = scrapy.Field()
    houses      = scrapy.Field()
    mansion_name_list = scrapy.Field()
    mansion_name_kana = scrapy.Field()
    primary_school = scrapy.Field()
    middile_school = scrapy.Field()
    old_bunjyo     = scrapy.Field()
    cons_company   = scrapy.Field()
    trafficStringRaw = scrapy.Field()

class T23RoomItem(scrapy.Item):
    url = scrapy.Field()
    mansion_id = scrapy.Field()
    rental = scrapy.Field()
    sale = scrapy.Field()

class GuideItem(scrapy.Item):
    cid = scrapy.Field()

class GuideItem1(GuideItem):
    prefecture = scrapy.Field()
    city       = scrapy.Field()
    kokusei    = scrapy.Field()
    daicho     = scrapy.Field()
    area       = scrapy.Field()
    gov        = scrapy.Field()

class GuideItem2(GuideItem):
    weather = scrapy.Field()
    #industry = scrapy.Field()

class GuideItem3(GuideItem):
    public = scrapy.Field()
    #garbage = scrapy.Field()
    safety = scrapy.Field()
    culture = scrapy.Field()

class GuideItem4(GuideItem):
    support = scrapy.Field()
    #marriage = scrapy.Field()
    nurture = scrapy.Field()

class GuideItem5(GuideItem):
    edu_kinder = scrapy.Field()
    edu_primary = scrapy.Field()
    edu_middle = scrapy.Field()
    edu_infra = scrapy.Field()
    edu_senior = scrapy.Field()

class GuideItem6(GuideItem):
    medical = scrapy.Field()
    care = scrapy.Field()

class GuideItem7(GuideItem):
    land_price = scrapy.Field()

class HomesMapMansionItem(scrapy.Item):
    basis_pkey = scrapy.Field()

    building_id          = scrapy.Field()
    building_name        = scrapy.Field()
    building_type        = scrapy.Field()
    year_built           = scrapy.Field()
    full_address         = scrapy.Field()
    floor_count          = scrapy.Field()
    unit_count           = scrapy.Field()
    near_stations        = scrapy.Field()

    pref_id              = scrapy.Field()
    city_id              = scrapy.Field()
    town_id              = scrapy.Field()
    address_id           = scrapy.Field()

    assessment_status    = scrapy.Field()
    assessed_min_price   = scrapy.Field()
    assessed_max_price   = scrapy.Field()

    display_price_status = scrapy.Field()
    display_status       = scrapy.Field()

    lat                  = scrapy.Field()
    lng                  = scrapy.Field()

    has_photo            = scrapy.Field()
    photo_type           = scrapy.Field()
    photo_file_path      = scrapy.Field()

    modify_date          = scrapy.Field()

class HomesMapRoomItem(scrapy.Item):
    basis_pkey = scrapy.Field()

    building_id          = scrapy.Field()
    building_name        = scrapy.Field()
    building_type        = scrapy.Field()
    year_built           = scrapy.Field()
    full_address         = scrapy.Field()
    floor_count          = scrapy.Field()
    unit_count           = scrapy.Field()
    near_stations        = scrapy.Field()

    unit_id              = scrapy.Field()
    unit_name            = scrapy.Field()
    room_floor           = scrapy.Field()
    window_angle         = scrapy.Field()
    balcony_area         = scrapy.Field()
    unit_area            = scrapy.Field()
    floor_plan           = scrapy.Field()
    publish_prices       = scrapy.Field()

    pref_id              = scrapy.Field()
    city_id              = scrapy.Field()
    town_id              = scrapy.Field()
    address_id           = scrapy.Field()

    assessed_price       = scrapy.Field()
    assessed_model       = scrapy.Field()
    assessment_status    = scrapy.Field()
    assessed_min_price   = scrapy.Field()
    assessed_max_price   = scrapy.Field()

    display_price_status = scrapy.Field()
    display_status       = scrapy.Field()

    lat                  = scrapy.Field()
    lng                  = scrapy.Field()

    has_photo            = scrapy.Field()
    photo_type           = scrapy.Field()
    photo_file_path      = scrapy.Field()
    
    modify_date          = scrapy.Field()
