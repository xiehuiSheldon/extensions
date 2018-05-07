import scrapy
import re
from ..items import TagItem, PosterItem, CategoryItem


class TagCategorySpider(scrapy.Spider):
    name = 'tag_category'
    allowed_domains = ['chrome.google.com']

    start_urls = ['http://chrome.google.com/webstore/category/extensions']

    def parse(self, response):
        all_content = response.xpath('//script[@id="cws-model-data"]/text()').extract()[0]

        #获取tags的内容
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
        #测试数据
        poster = PosterItem()
        poster['poster_path'] = "test"
        poster['ext_id'] = 1
        poster['weight'] = 0
        yield poster

        #获取插件类型数据
        x = 0
        #谷歌产品这个类型单独获取，有问题，1,这个类别不总是排在第一个？2,怎么把空的hot_picks插进去？
        cat_google_regex = r"""(?mx)
        \[\"(ext/                    #以["ext/开头的字符串，第一行作为一个个分组
        [^\"\]]+?[Gg]oogle)\",       #在同一个双引号内、方括号中有google这个词
        \"([^\"]+?)\",               #获取code_id 和 name
        """
        category = CategoryItem()
        cat_google = re.search(cat_google_regex, all_content)
        category['name'] = cat_google.group(2)
        category['code_id'] = cat_google.group(1)
        x += 1
        category['weight'] = x
        category['hot_picks'] = {"info": "null", "title": "null", "photo_url": "null"}
        yield category

        cat_line_regex = r"""(?mx)
        \[                          #以["ext/开头，以infiniteWall结尾的字符串
        \"(ext/[^\"]+?)\",          #获取code_id
        \"([^\"]+?)\"               #获取name
        [^\]]+?\]\n,                #至第一行结束
        \[                          #第二行开始
        [^,\]]*?,                   #匹配第一个逗号
        \"([^\"]+?)\",              #匹配第二个逗号，获取引号中的内容
        [^,\]]*?,                   #匹配第三个逗号
        [^,\]]*?,                   #匹配第四个逗号
        [^,\]]*?,                   #匹配第五个逗号
        [^,\]]*?,                   #匹配第六个逗号
        [^,\]]*?,                   #匹配第七个逗号
        \"([^\"]+?)\"               #匹配第八个逗号，获取引号中的内容
        \]\n,                       #第二行结束
        \[\"infiniteWall            #以此结尾作为区分标志
        """

        for cat_iter in re.finditer(cat_line_regex, all_content):
            category = CategoryItem()
            category['name'] = cat_iter.group(2)
            category['code_id'] = cat_iter.group(1)
            x += 1
            category['weight'] = x
            category['hot_picks'] = {"info": cat_iter.group(4), "title": cat_iter.group(3), "photo_url": "test"}
            yield category


