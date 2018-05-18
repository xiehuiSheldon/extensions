import scrapy
import re

from ..items import TagItem


class TagsSpider(scrapy.Spider):
    name = 'tags'
    allowed_domains = ['chrome.google.com']

    start_urls = ['http://chrome.google.com/webstore/category/extensions']

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
        x = 0
        for tag_iter in re.finditer(tag_line_regex, tag_con):
            tag = TagItem()
            tag['name'] = tag_iter.group(1)
            tag['code_id'] = tag_iter.group(2)
            tag['descript'] = tag_iter.group(3)
            x += 1
            tag['weight'] = x
            yield tag