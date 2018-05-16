# -*- coding: utf-8 -*-
import scrapy
import re
import random

from .parse_ext import Parser


class MoreExtSpider(scrapy.Spider):
    name = 'more_ext'
    allowed_domains = ['chrome.google.com']
    start_urls = ['https://chrome.google.com/webstore/category/extensions']

    def parse(self, response):
        all_content = response.xpath('//script[@id="cws-model-data"]/text()').extract()[0]

        first_url = r'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=US&pv=20180301&mce=atf%2Cpii%2' \
                    r'Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma%2' \
                    r'Cpot%2Cevt%2Cigb&requestedCounts=infiniteWall%3A92%3A0%3Afalse&token=featured%3A0%{change1}%3' \
                    r'A7%3Afalse%2Cmcol%23top_picks_{code_id2}%3A0%{change2}%3A11%3Atrue&category=ext%2F{code_id1}' \
                    r'&_reqid={reqid}&rt=j'

        other_url_base = r'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=US&pv=20180301&mce=atf%2Cpii%2' \
                         r'Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma%2' \
                         r'Cpot%2Cevt%2Cigb&requestedCounts=infiniteWall%3A{{page_limit}}%3A0%3Afalse&token=featured' \
                         r'%3A0%{change1}%3A7%3Afalse%2Cmcol%23top_picks_{code_id2}%3A0%{change2}%3A11%3Atrue%2' \
                         r'CinfiniteWall%3A0%{{change3}}%3A{{page_start}}%3Afalse&category=ext%2F{code_id1}' \
                         r'&_reqid={{reqid}}&rt=j'

        cat_line_regex = r'\[\"(ext/[^\"]+?)\"'

        for cat_iter in re.finditer(cat_line_regex, all_content):
            # 对每一个种类的插件设置初始url,先确定要改变的数据的值
            category_code_id = cat_iter.group(1)
            code_id1 = re.split(r'/', category_code_id)[1]
            code_id2 = re.search(r'\d+-(.+)', code_id1).group(1)
            val_change1 = 405000000 + int(random.random() * 1000000)
            val_change2 = val_change1 + 1
            reqid = 100000 + int(random.random() * 200000)
            val_change3 = val_change1 + 2

            url = first_url.format(
                code_id1=code_id1,
                code_id2=code_id2,
                change1=str(val_change1),
                change2=str(val_change2),
                reqid=str(reqid),
            )
            other_url_trans = other_url_base.format(
                code_id1=code_id1,
                code_id2=code_id2,
                change1=str(val_change1),
                change2=str(val_change2),
            )
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
            }
            meta = {
                'other_url_trans': other_url_trans,
                'reqid': reqid,
                'page_limit': 92,
                'page_start': 0,
                'change3': val_change3,
            }
            yield scrapy.Request(url, method='POST', headers=headers, meta=meta, callback=self.parse_list)


    # 通过解析ajax的返回文本，提取每个种类下的插件url list,提取每个url中插件的code_id,拼上base_url，发送插件详情请求
    def parse_list(self, response):
        base_url = 'https://chrome.google.com/webstore/ajax/detail?hl=zh-CN&gl=US&pv=20180301&mce=atf' \
                   '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac' \
                   '%2Cfcf%2Crma&id={ext_code_id}&container=CHROME&_reqid={reqid}&rt=j'

        ext_url_regex = r'\"(https://chrome\.google\.com/webstore/detail[^\"]+?)\"'
        for m in re.finditer(ext_url_regex, response.text):
            ext_url = m.group(1)
            ext_code_id = re.split(r'/', ext_url)[-1]
            # url = re.sub(r':change1:', ext_code_id, base_url)
            reqid = 100000 + int(random.random()*200000)
            # url = re.sub(r':change2:', str(reqid), url)
            url = base_url.format(ext_code_id=ext_code_id, reqid=str(reqid))
            yield scrapy.Request(url, method='POST', dont_filter=False, callback=self.parse_ext_detail)

        if re.search(ext_url_regex, response.text):
            other_url_trans = response.meta.get('other_url_trans')
            page_limit = response.meta.get('page_limit')
            page_start = response.meta.get('page_start') + page_limit
            # 往后都确定为96
            page_limit = 96
            reqid = response.meta.get('reqid') + 300000
            val_change3 = response.meta.get('change3')

            other_url = other_url_trans.format(
                page_limit=str(page_limit),
                page_start=str(page_start),
                reqid=str(reqid),
                change3=str(val_change3),
            )
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
            }
            meta = {
                'other_url_trans': other_url_trans,
                'reqid': reqid,
                'page_limit': page_limit,
                'page_start': page_start,
                'change3': val_change3,
            }
            yield scrapy.Request(other_url, method='POST', headers=headers, meta=meta, callback=self.parse_list)

    # 进入插件详情页
    def parse_ext_detail(self, response):
        content = response.text
        top = 0
        parser = Parser(content, top)
        yield parser.parse_detail()