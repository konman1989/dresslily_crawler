# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DresslilyScrapyProduct(scrapy.Item):
    product_id = scrapy.Field()
    product_url = scrapy.Field()
    product_name = scrapy.Field()
    original_price = scrapy.Field()
    rating = scrapy.Field()
    discount = scrapy.Field()
    discount_price = scrapy.Field()
    product_info = scrapy.Field()


class DresslilyScrapyReview(scrapy.Item):
    product_id = scrapy.Field()
    rating = scrapy.Field()
    timestamp = scrapy.Field()
    text = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()