# -*- coding: utf-8 -*-


import scrapy


class TagItem(scrapy.Item):
    name = scrapy.Field()
    code_id = scrapy.Field()
    descript = scrapy.Field()
    weight = scrapy.Field()


class PosterItem(scrapy.Item):
    id = scrapy.Field()
    poster_path = scrapy.Field()
    ext_id = scrapy.Field()
    weight = scrapy.Field()


class CategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    code_id = scrapy.Field()
    weight = scrapy.Field()
    hot_picks = scrapy.Field()


class ExtensionItem(scrapy.Item):
    id = scrapy.Field()
    category_id = scrapy.Field()
    code_id = scrapy.Field()
    name = scrapy.Field()
    short_intro = scrapy.Field()
    thumbnail_path = scrapy.Field()
    rank = scrapy.Field()
    download_count = scrapy.Field()
    free = scrapy.Field()
    top = scrapy.Field()
    detail_info = scrapy.Field()
    related_ext = scrapy.Field()
    update_time = scrapy.Field()
