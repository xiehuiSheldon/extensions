# -*- coding: utf-8 -*-
import scrapy
import re
import json
import random

from .scrape_categories import ScrapeCategories
from .parse_dispatch import ParserDispatch
from ..items import RelatedExtItem


class MoreExtSpider(scrapy.Spider):
    name = 'more_ext'
    allowed_domains = ['chrome.google.com']

    def start_requests(self):
        first_url = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301' \
                    '&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm' \
                    '%2Cac%2Chot%2Cmac%2Cfcf%2Crma%2Cpot%2Cevt%2Cigb%2Crae%2Cshr' \
                    '&requestedCounts=infiniteWall%3A{count}%3A0%3Afalse&token=featured' \
                    '%3A0%40{number1}%3A7%3Afalse%2Cmcol%23{top_picks_code_id}%3A0' \
                    '%40{number2}%3A11%3Atrue&category={long_code_id}&_reqid={reqid}&rt=j'

        other_url_base = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301&mce=atf' \
                         '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot' \
                         '%2Cmac%2Cfcf%2Crma%2Cpot%2Cevt%2Cigb%2Crae%2Cshr&requestedCounts=infiniteWall' \
                         '%3A{{count}}%3A0%3Afalse&token=featured%3A0%40{number1}%3A7%3Afalse%2Cmcol' \
                         '%23{top_picks_code_id}%3A0%40{number2}%3A11%3Atrue%2CinfiniteWall' \
                         '%3A0%40{number3}%3A{{token}}%3Afalse&category={long_code_id}&_reqid={{reqid}}&rt=j'

        cat = ScrapeCategories('https://chrome.google.com/webstore/category/extensions')
        for category in cat.categories:
            # if category.get('top_picks_code_id') == 'collection/top_picks_news':
            if category.get('top_picks_code_id'):
                # 1,发送item请求
                count = 92
                token = 0
                number1 = 11000000 + int(random.random() * 1000000)
                top_picks_code_id = re.split(r'/', category.get('top_picks_code_id'))[1]
                number2 = number1 + 1
                number3 = number1 + 2
                long_code_id = category.get('long_code_id')
                reqid = 4000000 + int(random.random() * 8000000)
                url = first_url.format(
                    count=count,
                    number1=number1,
                    top_picks_code_id=top_picks_code_id,
                    number2=number2,
                    long_code_id=long_code_id,
                    reqid=reqid,
                )
                other_url_trans = other_url_base.format(
                    number1=number1,
                    top_picks_code_id=top_picks_code_id,
                    number2=number2,
                    number3=number3,
                    long_code_id=long_code_id,
                )
                meta = {
                    'category_id': category.get('weight'),
                    'other_url_trans': other_url_trans,
                    'count': count,
                    'token': token,
                    'reqid': reqid,
                }
                yield scrapy.Request(url, method='POST', meta=meta, callback=self.parse_list)

    # 通过解析ajax的返回文本，提取每个种类下的插件url list,提取每个url中插件的code_id,拼上base_url，发送插件详情请求
    def parse_list(self, response):
        category_id = response.meta.get('category_id')

        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'

        json_data = json.loads(re.sub('^\)\]\}\'\n', r'', response.text))
        for ext in json_data[0][1][1]:
            ext_code_id = re.split(r'/', ext[37])[-1]
            reqid = 100000 + int(random.random() * 200000)
            url = base_url.format(ext_code_id=ext_code_id, reqid=str(reqid))
            meta = {'category_id': category_id}
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
                'category_id': category_id,
                'other_url_trans': other_url_trans,
                'count': count,
                'token': token,
                'reqid': reqid,
            }
            yield scrapy.Request(other_url, method='POST', meta=meta, callback=self.parse_list)

    # 进入插件详情页
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