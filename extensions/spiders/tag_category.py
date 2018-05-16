import scrapy
import re

from ..items import TagItem, PosterItem, CategoryItem


class TagCategorySpider(scrapy.Spider):
    name = 'tag_category'
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

        # 获取插件类型数据
        x = 0
        cat_line_regex = re.compile(r'\[\"(ext/[^\"]+?)\",\"([^\"]+?)\".+\n,(.+)\n')
        for cat_iter in re.finditer(cat_line_regex, all_content):
            category = CategoryItem()
            category_code_id = cat_iter.group(1)
            category['code_id'] = category_code_id
            category['name'] = cat_iter.group(2)
            second_line = cat_iter.group(3)
            x += 1
            category['weight'] = x
            by_google_regex = re.compile(r'by-google')
            if re.search(by_google_regex, category_code_id):
                category['hot_picks'] = "null"
            else:
                second_line = re.sub(r',null', r'', second_line)
                second_line = eval(second_line)
                photo_url = second_line[0]
                photo_url = re.sub(r'mcol#', '', photo_url)
                photo_url = '/category/hot_picks/' + photo_url + '.png'
                category['hot_picks'] = {"info": second_line[-1], "title": second_line[1], "photo_url": photo_url}
            yield category


