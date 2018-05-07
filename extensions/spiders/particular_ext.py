# -*- coding: utf-8 -*-
import scrapy
from ..items import ExtensionItem
import re
import json


class ParticularExtSpider(scrapy.Spider):
    name = 'particular_ext'
    allowed_domains = ['chrome.google.com']
    start_urls =['https://chrome.google.com/webstore/detail/amazon-publisher-studio-e/clihldpfnfandacppigjpkmkaaemlfie']

    def parse(self, response):
        url = 'https://chrome.google.com/webstore/ajax/detail?' \
              'hl=zh-CN&gl=TW&pv=20180301&mce=atf%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd' \
              '%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2Cmac%2Cfcf%2Crma&id=clihldpfnfandacppigjpkmkaaemlfie' \
              '&container=CHROME&_reqid=271667&rt=j'
        yield scrapy.Request(url, method='POST', callback=self.parse_ext_detail)


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

        # 简短介绍
        pattern = r'(?m)' + mark + r'.+\"([^\"]+?)\",[^,]+$'
        m = re.search(pattern, content)
        if m:
            ext['short_intro'] = m.group(1)

        # 所属类别--#评分
        pattern = mark + r'[^\n]+?\n,[^,]+?,\"([^\"]+?)\",\"([^\"]+?)\",\"[^\"]+?\",([^,]+?),'
        m = re.search(pattern, content)
        if m:
            ext['detail_info']['type_name'] = m.group(2)
            ext['rank'] = m.group(3)

        # 是否免费
        pattern = mark + r'[^\n]+?\n.+?\"[^\"]+?free[^\"]+?\",[^,]+?,\"([^\"]+?)\"'
        m = re.search(pattern, content)
        if m:
            is_free = m.group(1)
            if re.search(r'(^免费$)|(^free$)', is_free):
                ext['free'] = 1
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
            ext['detail_info']['website'] = six_line_element[0]
            ext['download_count'] = re.sub(',', '', six_line_element[1])
            ext['detail_info']['version'] = six_line_element[3]
            ext['update_time'] = six_line_element[4]
            ext['detail_info']['language'] = six_line_element[5]

        # 总结icons
        pattern = r',([^,]+?icons[^{]+?{[^}]+?})'
        m = re.search(pattern, content)
        if m:
            s = m.group(1)
            s = re.sub(r'\s|\\n|\\', '', s)
            j = json.loads('{' + s + '}')
            ext['detail_info']['icons'] = j.get('icons')

        # 没找到的key暂为null
        #ext['code_id'] = 'gojbdfnpnhogfdgjbigejoaolejmgdhk'
        ext['category_id'] = 2 # 类别不能是不存在，因为有外键关联
        ext['thumbnail_path'] = 'null'
        ext['top'] = 0
        ext['related_ext'] = 0

        yield ext