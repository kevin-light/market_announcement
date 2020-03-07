# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MarketAnnouncementItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AnnouncementItem(scrapy.Item):

    annc_code = scrapy.Field()
    annc_url = scrapy.Field()
    annc_title = scrapy.Field()
    annc_data = scrapy.Field()
    annc_date = scrapy.Field()
    annc_now_date = scrapy.Field()