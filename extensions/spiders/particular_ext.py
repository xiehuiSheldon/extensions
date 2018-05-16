# -*- coding: utf-8 -*-
import scrapy
import random

from .parse_ext import Parser


class ParticularExtSpider(scrapy.Spider):
    name = 'particular_ext'
    allowed_domains = ['chrome.google.com']
    start_urls =['https://chrome.google.com/webstore/detail/halo-new-tab-speed-dialex/dlifjiogddhoeolhhdcbboapciojnmoi']

    def parse(self, response):
        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'
        ext_code_id = 'dlifjiogddhoeolhhdcbboapciojnmoi'
        reqid = 100000 + int(random.random() * 200000)
        url = base_url.format(ext_code_id=ext_code_id, reqid=str(reqid))
        yield scrapy.Request(url, method='POST', callback=self.parse_ext_detail)


    def parse_ext_detail(self, response):
        content = response.text
        with open('tmp/one_ext.txt', 'w', encoding='utf-8') as file:
            file.write(content)
        top = 1
        parser = Parser(content, top)
        # print(parser.parse_detail())
        yield parser.parse_detail()