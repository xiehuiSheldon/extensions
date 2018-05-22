# -*- coding: utf-8 -*-
import scrapy
import random
import re
import json

from .parse_dispatch import ParserDispatch
from ..items import RelatedExtItem


class ParticularExtSpider(scrapy.Spider):
    name = 'particular_ext'
    allowed_domains = ['chrome.google.com']
    # 相应改变1
    start_urls =['https://chrome.google.com/webstore/detail/readlang-web-reader/odpdkefpnfejbfnmdilmfhephfffmfoh']

    def parse(self, response):
        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'
        # 响应改变2
        ext_code_id = 'odpdkefpnfejbfnmdilmfhephfffmfoh'
        reqid = 100000 + int(random.random() * 200000)
        url = base_url.format(ext_code_id=ext_code_id, reqid=reqid)
        yield scrapy.Request(url, method='POST', callback=self.parse_ext_detail)

    def parse_ext_detail(self, response):
        json_date = json.loads(re.sub('^\)\]\}\'\n', r'', response.text))
        ext = ParserDispatch.parse_ext(json_date)
        ext['detail_info'] = ParserDispatch.parse_detail_info(json_date)
        ext['related_ext'] = ParserDispatch.parse_related_ext(json_date)
        # test, 要改
        ext['category_id'] = 9
        # test, 要改
        ext['top'] = 1
        yield ext
        for rel_ext in ext['related_ext']:
            rel_ext_item = RelatedExtItem(
                owner_code_id=ext['code_id'],
                related_code_id=rel_ext.get('code_id')
            )
            yield rel_ext_item