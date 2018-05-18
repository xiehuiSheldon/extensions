# -*- coding: utf-8 -*-
import re
import random

import scrapy

from .scrape_categories import ScrapeCategories
from .parse_ext import Parser
from ..items import CategoryItem


class TopPicksSpider(scrapy.Spider):
    name = 'top_picks'
    allowed_domains = ['chrome.google.com']

    def start_requests(self):
        base_url = r'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=US&pv=20180301' \
                   r'&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2C' \
                   r'ac%2Chot%2Cmac%2Cfcf%2Crma%2Cpot%2Cevt%2Cigb&count=25&token=0%401620439&marquee=true' \
                   r'&category=collection%2F{mark}&sortBy=0&container=CHROME&_reqid={reqid}&rt=j'

        cat = ScrapeCategories('https://chrome.google.com/webstore/category/extensions')
        for category in cat.categories:
            category_item = CategoryItem({k: category[k] for k in ('name', 'code_id', 'weight')})
            if category['second_line']:
                category_item['hot_picks'] = {
                    "info": category['second_line'][-1],
                    "title": category['second_line'][1],
                }
                # 发送新的请求
                reqid = 100000 + int(random.random() * 200000)
                mark = re.sub(r'mcol#', '', category['second_line'][0])
                url = base_url.format(mark=mark, reqid=str(reqid))
                meta = {'category_item': category_item, 'mark': mark}
                yield scrapy.Request(url, method='POST', meta=meta, callback=self.parse_list)
            else:
                url = 'https://chrome.google.com/robots.txt'
                meta = {'category_item': category_item}
                yield scrapy.Request(url, meta=meta, callback=self.parse_list)

    def parse_list(self, response):
        category_item = response.meta.get('category_item')
        if 'hot_picks' not in category_item:
            yield category_item
            return
        mark = response.meta.get('mark')
        photo_regex = r'\".*?@.*?\",(\[[^\[\]]+?\])'
        photo_detail = re.search(photo_regex, response.text).group(1)
        if photo_detail:
            # 获取图片URL及颜色
            photo_detail = eval(photo_detail)
            photo_url_net = photo_detail[0]
            photo_color = photo_detail[2]
            yield {'image_urls': photo_url_net}
            # 生成本地图片路径
            photo_url = '/category/hot_picks/' + mark + '.png'
            category_item['hot_picks']['photo_url'] = photo_url
            category_item['hot_picks']['photo_color'] = photo_color
            yield category_item

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