# -*- coding: utf-8 -*-
import re
import json
import random
import scrapy

from .parse_dispatch import ParserDispatch
from .scrape_categories import ScrapeCategories
from ..items import RelatedExtItem, CategoryItem


class MoreExtGoogleSpider(scrapy.Spider):
    name = 'more_ext_google'
    allowed_domains = ['chrome.google.com']

    def start_requests(self):
        first_url = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301' \
                    '&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2C' \
                    'ctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma&count={count}&marquee=true&category={long_code_id}' \
                    '&sortBy=0&container=CHROME&_reqid={reqid}&rt=j'
        other_url_base = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301' \
                         '&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot' \
                         '%2Cmac%2Cfcf%2Crma%2Cpot%2Cevt%2Cigb&count={{count}}&token={{token}}%40{number1}' \
                         '&category={long_code_id}&sortBy=0&container=CHROME&_reqid={{reqid}}&rt=j'
        cat = ScrapeCategories('https://chrome.google.com/webstore/category/extensions')
        for category in cat.categories:
            if not category.get('top_picks_code_id'):
                category_item = CategoryItem({k: category[k] for k in ('name', 'code_id', 'weight')})
                # 1,发送item请求
                count = 25
                token = 0
                number1 = 11000000 + int(random.random() * 1000000)
                long_code_id = category.get('long_code_id')
                reqid = 400000 + int(random.random() * 800000)
                url = first_url.format(
                    count=count,
                    long_code_id=long_code_id,
                    reqid=reqid,
                )
                other_url_trans = other_url_base.format(
                    number1=number1,
                    long_code_id=long_code_id,
                )
                meta = {
                    'category_count': 0,
                    'category_item': category_item,
                    'other_url_trans': other_url_trans,
                    'count': count,
                    'token': token,
                    'reqid': reqid,
                }
                yield scrapy.Request(url, method='POST', meta=meta, callback=self.parse_list)

    def parse_list(self, response):
        category_count = response.meta.get('category_count')
        category_item = response.meta.get('category_item')
        if category_count == 0:
            category_count += 1
            yield category_item
        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'
        json_data = json.loads(re.sub('^\)\]\}\'\n', r'', response.text))
        for ext in json_data[0][1][1]:
            ext_code_id = re.split(r'/', ext[37])[-1]
            reqid = 100000 + int(random.random() * 200000)
            url = base_url.format(ext_code_id=ext_code_id, reqid=str(reqid))
            meta = {'category_id': category_item.get('weight')}
            yield scrapy.Request(url, method='POST', meta=meta, callback=self.parse_ext_detail)

        # 一次请求无法完成时，再发后续请求
        if json_data[0][1][1]:
            other_url_trans = response.meta.get('other_url_trans')
            count = response.meta.get('count')
            token = response.meta.get('token')
            reqid = response.meta.get('reqid')
            other_url = other_url_trans.format(
                token=token + count,
                count=96,
                reqid=reqid + 200000,
            )
            meta = {
                'category_count': category_count,
                'category_item': category_item,
                'other_url_trans': other_url_trans,
                'count': count,
                'token': token,
                'reqid': reqid,
            }
            yield scrapy.Request(other_url, method='POST', meta=meta, callback=self.parse_list)

    def parse_ext_detail(self, response):
        # test, 要改!!!
        category_id = response.meta.get('category_id')
        json_date = json.loads(re.sub('^\)\]\}\'\n', r'', response.text))
        ext = ParserDispatch.parse_ext(json_date)
        ext['detail_info'] = ParserDispatch.parse_detail_info(json_date)
        ext['related_ext'] = ParserDispatch.parse_related_ext(json_date)
        # test, 要改!!!
        ext['category_id'] = category_id
        # test, 要改!!!
        ext['top'] = 0
        yield ext
        for rel_ext in ext['related_ext']:
            rel_ext_item = RelatedExtItem(
                owner_code_id=ext['code_id'],
                related_code_id=rel_ext.get('code_id')
            )
            yield rel_ext_item