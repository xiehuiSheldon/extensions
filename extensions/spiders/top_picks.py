# -*- coding: utf-8 -*-
import scrapy
import re
import random

from .parse_ext import Parser


class TopPicksSpider(scrapy.Spider):
    name = 'top_picks'
    allowed_domains = ['chrome.google.com']
    start_urls = ['https://chrome.google.com/webstore/category/extensions']

    # 通过解析主页获取每个类型的category_code_id，拼上base_url发送ajax请求
    def parse(self, response):
        all_content = response.xpath('//script[@id="cws-model-data"]/text()').extract()[0]
        # 注意修改地区，TW->US
        '''
        base_url = r'https://chrome.google.com/webstore/ajax/item?' \
                   r'hl=zh-CN&gl=US&pv=20180301&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp' \
                   r'%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma&count=25&marquee=true&category=collection' \
                   r'%2Ftop_picks_{code_id}&sortBy=0&container=CHROME&_reqid={reqid}&rt=j'
        '''
        base_url = r'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=US&pv=20180301' \
                   r'&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2C' \
                   r'ac%2Chot%2Cmac%2Cfcf%2Crma%2Cpot%2Cevt%2Cigb&count=25&token=0%401620439&marquee=true' \
                   r'&category=collection%2Ftop_picks_{code_id}&sortBy=0&container=CHROME&_reqid={reqid}&rt=j'

        # category_code_id标识该类型，拼上base_url,获取每一个类型的热门精选的插件
        cat_line_regex = r'\[\"(ext/[^\"]+?)\"'
        # 注意google产品没有热门精选
        for cat_iter in re.finditer(cat_line_regex, all_content):
            category_code_id = cat_iter.group(1)
            by_google_regex = re.compile(r'by-google')
            if not re.search(by_google_regex, category_code_id):
                code_id = re.search(r'\d+-(.+)$', category_code_id).group(1)
                reqid = 100000 + int(random.random() * 200000)
                url = base_url.format(code_id=code_id, reqid=str(reqid))
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
                }
                yield scrapy.Request(url, method='POST', headers=headers, callback=self.parse_list)

    def parse_list(self, response):
        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'

        ext_url_regex = r'\"(https://chrome\.google\.com/webstore/detail[^\"]+?)\"'
        for m in re.finditer(ext_url_regex, response.text):
            ext_url = m.group(1)
            ext_code_id = re.split(r'/', ext_url)[-1]
            reqid = 100000 + int(random.random()*200000)
            url = base_url.format(ext_code_id=ext_code_id, reqid=str(reqid))
            yield scrapy.Request(url, method='POST', dont_filter=False, callback=self.parse_ext_detail)

    # 进入插件详情页
    def parse_ext_detail(self, response):
        content = response.text
        top = 1
        parser = Parser(content, top)
        yield parser.parse_detail()