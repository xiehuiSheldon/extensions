# -*- coding: utf-8 -*-
import scrapy
import re
import random

from ..items import TagItem, TagsExtensionsItem


class TagsSpider(scrapy.Spider):
    name = 'tags'
    allowed_domains = ['chrome.google.com']

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        }
        url = 'http://chrome.google.com/webstore/category/extensions'
        yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        all_content = response.xpath('//script[@id="cws-model-data"]/text()').extract()[0]
        # 获取tags的内容
        start_pos = 0
        end_pos = all_content.find('infiniteWall')
        tag_con = all_content[start_pos:end_pos]
        tag_line_regex = r"""(?mx)
        ^,\[\"mcol.+?\",           #以此开头
        \"([^\"]+?)\",             #name
        .*?,                       #第三行，一般是1
        \"([^\"]+?)\",             #code_id
        .*?,                       #第五行，一般是1
        .*?,                       #第六行，一般是null
        .*?,                       #第七行，一般是null
        \"([^\"]*?)\"              #descript，可以没有描述，故用*
        ]$                         #以此结尾
        """
        first_url = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301&mce=atf' \
                    '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2' \
                    'Cmac%2Cfcf%2Crma%2Cirt%2Cscm%2Cqso%2Chrb%2Crae%2Cshr%2Cdda%2Cigb%2Cpot%2Cevt' \
                    '&count={count}&token={token}%40{number}&marquee=true&category={code_id}&sortBy=0' \
                    '&container=CHROME&_reqid={reqid}&rt=j'
        other_url_base = 'https://chrome.google.com/webstore/ajax/item?hl=zh-CN&gl=TW&pv=20180301&mce=atf' \
                         '%2Cpii%2Crtr%2Crlb%2Cgtc%2Chcn%2Csvp%2Cwtd%2Cnrp%2Chap%2Cnma%2Cctm%2Cac%2Chot%2' \
                         'Cmac%2Cfcf%2Crma%2Cirt%2Cscm%2Cqso%2Chrb%2Crae%2Cshr%2Cdda%2Cigb%2Cpot%2Cevt' \
                         '&count={{count}}&token={{token}}%40{number}&marquee=true&category={code_id}&sortBy=0' \
                         '&container=CHROME&_reqid={{reqid}}&rt=j'
        w = 0
        for tag_iter in re.finditer(tag_line_regex, tag_con):
            tag = TagItem()
            tag['name'] = tag_iter.group(1)
            tag['code_id'] = tag_iter.group(2)
            tag['descript'] = tag_iter.group(3)
            w += 1
            tag['weight'] = w
            yield tag

            # 设置每个标签的参数
            count = 25
            token = 0
            number = 50000 + int(random.random() * 150000)
            code_id = tag['code_id']
            reqid = 10000000 + int(random.random() * 20000000)
            url = first_url.format(
                count=count,
                token=token,
                number=number,
                code_id=code_id,
                reqid=reqid,
            )
            other_url_trans = other_url_base.format(
                number=number,
                code_id=code_id,
            )
            meta = {
                'tag_id': tag.get('weight'),
                'other_url_trans': other_url_trans,
                'count': count,
                'token': token,
                'reqid': reqid,
            }
            yield scrapy.Request(url, method='POST', meta=meta, callback=self.parse_get_ext_id)

    def parse_get_ext_id(self, response):
        tag_id = response.meta.get('tag_id')
        ext_regex = re.compile(r'\"[a-z]{20,}?\"')
        exts_set = set(re.findall(ext_regex, response.text))
        for ext_code_id in exts_set:
            tag_ext_item = TagsExtensionsItem(tag_id=tag_id, ext_code_id=ext_code_id)
            yield tag_ext_item

        # 一次请求无法完成时，再发后续请求
        if exts_set:
            other_url_trans = response.meta.get('other_url_trans')
            count = response.meta.get('count')
            token = response.meta.get('token')
            reqid = response.meta.get('reqid')
            token = token + count
            count = 96
            reqid = reqid + 200000
            other_url = other_url_trans.format(
                token=token,
                count=count,
                reqid=reqid,
            )
            meta = {
                'tag_id': tag_id,
                'other_url_trans': other_url_trans,
                'count': count,
                'token': token,
                'reqid': reqid,
            }
            yield scrapy.Request(other_url, method='POST', meta=meta, callback=self.parse_get_ext_id)