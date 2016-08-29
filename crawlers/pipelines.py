# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
import pymongo

class CrawlersPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        spider_name = spider.name

        if spider_name == 'ieshil':
            try:
                item['prefecture']
                self.db.ieshil_mansion.update_one({'mansion_id': item['mansion_id']}, {'$set': dict(item)}, True)
            except KeyError:
                self.db.ieshil_room.update_one({'mansion_id': item["mansion_id"], 'floor': item['floor']}, {'$set': dict(item)}, True)

        elif spider_name == 't23m' or spider_name == 't23m_noise':
            try:
                item['name']
                self.db.t23_mansion.update_one(
                    {'mansion_id': item["mansion_id"]}, 
                    {
                        '$set': dict(item),
                        "$currentDate": {"lastModified": True}
                    }, True
                )
            except KeyError:
                self.db.t23_room.update_one(
                    {'mansion_id': item["mansion_id"]}, 
                    {
                        '$set': dict(item),
                        "$currentDate": {"lastModified": True}
                    }, True)
        elif spider_name == 'guide':
            self.db.guide.update_one({'cid': item['cid']}, {'$set': dict(item), "$currentDate": {"updated_at": True}}, True)
        elif spider_name == 'homes-map':
            try:
                item['unit_id']
                self.db.homesmap_room.update_one({'building_id': item['building_id'], 'unit_id': item['unit_id']}, {'$set': dict(item), "$currentDate": {"updated_at": True}}, True)
            except KeyError:
                self.db.homesmap_mansion.update_one({'basis_pkey': item['basis_pkey'], 'building_id': item['building_id']}, {'$set': dict(item), "$currentDate": {"updated_at": True}}, True)
        return item