# -*- coding: utf-8 -*-
import re
import json

from ..items import ExtensionItem
"""
这个方法写得不容易，可是并没有按json的思路来解析
只能舍弃了···
"""


class Parser:
    def __init__(self, content, top):
        self.content = content
        self.top = top

    # 进入插件详情页
    def parse_detail(self):
        ext = ExtensionItem()
        content = self.content
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
        pattern = r'(?m)' + mark + r'.+\"([^\"]+?)\",\[\[.+$'
        m = re.search(pattern, content)
        if m:
            ext['short_intro'] = m.group(1)
        else:
            ext['short_intro'] = "null"

        # 所属类别--#评分
        # pattern = mark + r'[^\n]+?\n,[^,]+?,\"([^\"]+?)\",\"([^\"]+?)\",\"[^\"]+?\",([^,]+?),'
        pattern = r'\"([^\"]+?)\",\"([^\"]+?)\",([0-5]\.\d{10,})'
        m = re.search(pattern, content)
        if m:
            ext['detail_info']['type_name'] = m.group(1)
            ext['rank'] = m.group(3)
        else:
            ext['detail_info']['type_name'] = "null"
            ext['rank'] = 0.0

        # 是否免费
        # pattern = mark + r'[^\n]+?\n.+?\"[^\"]+?free[^\"]+?\",[^,]+?,\"([^\"]+?)\"'
        pattern = r'\"(免费)|(FREE)\"'
        m = re.search(pattern, content)
        if m:
            ext['free'] = 1
        else:
            ext['free'] = 0

        # 详情介绍,#第六行内容，包括：网站、下载量、版本号、更新时间、语言
        # pattern = mark + r'([^\n]+?\n){5},\"([^\"]+?)\"([^\n]+?)\n'
        pattern = r'(?m)^,(?<!\\)\"(.+?)(?<!\\)\"(.+?年.+?月.+?日.+)$'
        m = re.search(pattern, content)
        if m:
            ext['detail_info']['detail_introduce'] = m.group(1)
            six_line_last = m.group(2)
            pattern = r'[^\"]+?\"([^\"]*?)\"'
            six_line_element = re.findall(pattern, six_line_last)
            try:
                ext['detail_info']['website'] = six_line_element[0]
                ext['download_count'] = re.sub(',', '', six_line_element[1])
                ext['detail_info']['version'] = six_line_element[3]
                ext['update_time'] = six_line_element[4]
                ext['detail_info']['language'] = six_line_element[5:]
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
            s = re.sub(r'\s|\\r|\\n|\\', '', s)
            try:
                j = json.loads('{' + s + '}')
                ext['detail_info']['icons'] = j.get('icons')
            except:
                ext['detail_info']['icons'] = "null"

        # 没找到的key暂为null
        # ext['code_id'] = 'gojbdfnpnhogfdgjbigejoaolejmgdhk'
        ext['category_id'] = 2  # 类别不能是不存在，因为有外键关联
        ext['thumbnail_path'] = "null"
        ext['top'] = self.top
        ext['related_ext'] = 0

        return ext