# -*- coding: utf-8 -*-
import scrapy
import re
import json
import random
from ..items import ExtensionItem


class ExtensionSpider(scrapy.Spider):
    name = 'extension'
    allowed_domains = ['chrome.google.com']
    start_urls = ['https://chrome.google.com/webstore/category/extensions']

    # 通过主页获取每个类型的category_code_id，拼上base_url发送ajax请求
    def parse(self, response):
        all_content = response.xpath('//script[@id="cws-model-data"]/text()').extract()[0]

        base_url = r'https://chrome.google.com/webstore/ajax/item?' \
                   'hl=zh-CN&gl=TW&pv=20180301&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%' \
                   '2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma&requestedCounts=featured%3A' \
                   '7%3A10%3Afalse%2Cmcol%23top_picks_:change2:%3A11%3A1%3Atrue&category=ext%2F:change1:' \
                   '&_reqid=154963&rt=j'

        # category_code_id标识该类型，拼上base_url,获取每一个类型的热门精选的插件
        cat_line_regex = r'\[\"(ext/[^\"]+?)\"'
        for cat_iter in re.finditer(cat_line_regex, all_content):
            category_code_id = cat_iter.group(1)
            if category_code_id:
                code_id1 = re.split(r'/', category_code_id)[1]
                code_id2 = re.search(r'\d+-(.+)', code_id1).group(1)
                url = re.sub(r':change1:', code_id1, base_url)
                url = re.sub(r':change2:', code_id2, url)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
                }
                yield scrapy.Request(url, method='POST', headers=headers, callback=self.parse_list)


    # 通过解析ajax的返回文本，提取每个种类下的插件url list,提取每个url中插件的code_id,拼上base_url，发送插件详情请求
    def parse_list(self, response):

        base_url = 'https://chrome.google.com/webstore/ajax/detail?' \
              'hl=zh-CN&gl=TW&pv=20180301&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd' \
              '%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma&id=:change1:' \
              '&container=CHROME&_reqid=:change2:&rt=j'

        ext_url_regex = r'\"(https://chrome\.google\.com/webstore/detail[^\"]+?)\"'
        for m in re.finditer(ext_url_regex, response.text):
            ext_url = m.group(1)
            ext_code_id = re.split(r'/', ext_url)[-1]
            url = re.sub(r':change1:', ext_code_id, base_url)
            reqid = 100000 + int(random.random()*200000)
            url = re.sub(r':change2:', str(reqid), url)
            yield scrapy.Request(url, method='POST', callback=self.parse_ext_detail)


    # 进入插件详情页
    def parse_ext_detail(self, response):
        ext = ExtensionItem()
        content = response.text
        mark = r'getitemdetailresponse'

        ext['detail_info'] = {}

        # code_id, name, 开发者
        pattern = mark + r'\",\[\[\"([^\"]+?)\",\"([^\"]+?)\",\"([^\"]+?)\"'
        m = re.search(pattern, content)
        if m:
            ext['code_id'] = m.group(1)
            ext['name'] = m.group(2)
            ext['detail_info']['developer'] = m.group(3)
        else:
            ext['code_id'] = "null"
            ext['name'] = "null"
            ext['detail_info']['developer'] = "null"

        # 简短介绍
        pattern = r'(?m)' + mark + r'.+\"([^\"]+?)\",[^,]+$'
        m = re.search(pattern, content)
        if m:
            ext['short_intro'] = m.group(1)
        else:
            ext['short_intro'] = "null"

        # 所属类别--#评分
        pattern = mark + r'[^\n]+?\n,[^,]+?,\"([^\"]+?)\",\"([^\"]+?)\",\"[^\"]+?\",([^,]+?),'
        m = re.search(pattern, content)
        if m:
            ext['detail_info']['type_name'] = m.group(2)
            ext['rank'] = m.group(3)
        else:
            ext['detail_info']['type_name'] = "null"
            ext['rank'] = 0.0

        # 是否免费
        pattern = mark + r'[^\n]+?\n.+?\"[^\"]+?free[^\"]+?\",[^,]+?,\"([^\"]+?)\"'
        m = re.search(pattern, content)
        if m:
            is_free = m.group(1)
            if re.search(r'(^免费$)|(^free$)', is_free):
                ext['free'] = 1
            else:
                ext['free'] = 0
        else:
            ext['free'] = 0

        # 详情介绍,#第六行内容，包括：网站、下载量、版本号、更新时间、语言
        pattern = mark + r'([^\n]+?\n){5},\"([^\"]+?)\"([^\n]+?)\n'
        m = re.search(pattern, content)
        if m:
            ext['detail_info']['detail_introduce'] = m.group(2)
            six_line_last = re.search(pattern, content).group(3)
            pattern = r'[^\"]+?\"([^\"]+?)\"'
            six_line_element = re.findall(pattern, six_line_last)
            try:
                ext['detail_info']['website'] = six_line_element[0]
                ext['download_count'] = re.sub(',', '', six_line_element[1])
                ext['detail_info']['version'] = six_line_element[3]
                ext['update_time'] = six_line_element[4]
                ext['detail_info']['language'] = six_line_element[5]
            except:
                ext['download_count'] = 0
                ext['update_time'] = "2018年5月5日"
        else:
            ext['download_count'] = 0
            ext['update_time'] = "2018年5月5日"

        # 总结icons
        pattern = r',([^,]+?icons[^{]+?{[^}]+?})'
        m = re.search(pattern, content)
        if m:
            s = m.group(1)
            s = re.sub(r'\s|\\n|\\', '', s)
            try:
                j = json.loads('{' + s + '}')
                ext['detail_info']['icons'] = j.get('icons')
            except:
                ext['detail_info']['icons'] = "null"

        # 没找到的key暂为null
        #ext['code_id'] = 'gojbdfnpnhogfdgjbigejoaolejmgdhk'
        ext['category_id'] = 2 # 类别不能是不存在，因为有外键关联
        ext['thumbnail_path'] = "null"
        ext['top'] = 0
        ext['related_ext'] = 0

        yield ext
