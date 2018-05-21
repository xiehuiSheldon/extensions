# -*- coding: utf-8 -*-
import scrapy


class MoreExtSpider(scrapy.Spider):
    name = 'more_ext_google'
    allowed_domains = ['chrome.google.com']

    def start_requests(self):
        pass

    def parse_list(self, response):
        pass

    def parse_ext_detail(self, response):
        pass