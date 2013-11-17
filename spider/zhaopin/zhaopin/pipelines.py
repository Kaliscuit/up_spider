# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
from twisted.enterprise import adbapi
from scrapy.http import Request
from scrapy.exceptions import DropItem
from scrapy.contrib.pipeline.images import ImagesPipeline
import time
import MySQLdb
import MySQLdb.cursors
import socket
import select
import sys
import os
import errno

class ZhaopinPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            db = 'test',
            user = 'root',
            passwd = 'mijack',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8',
            use_unicode = False
            )

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self, tx, item):
        if item.get('url'):
            tx.execute('insert into zhaopin (url, position, position_desc, requirements, company, company_desc, company_address, company_homepage, time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (item['url'], item['position'], item['position_desc'], item['requirements'], item['company'], item['company_desc'], item['company_address'], item['company_homepage'], item['time']))