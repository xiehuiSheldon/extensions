import scrapy
import re
import json

from ..items import PosterItem

"""
###
总结规律：
1，最好的办法就是找 @ 符号，整个extensions中出现的就很少
2，但是某些文本中也出现了，比如设置字体和邮件，为了排除这些，做如下：
3，设两个限定：
3.1，找到 getitemsresponse 及以后
3.2，再在 getitemsresponse 里面找 featured，就出现两处 featured
4，而两处 featured，一处是 @ 告知 featured 的结束限定符，一处就是结束限定。
如此，正则表达式就好写了。

pattern = r'(?s)getitemsresponse.*?featured:(?P<mark>\d+@\d+):.*?(?P<featured>\[\"featured\".*?\"(?P=mark)\".*?\])'
"""
class PostersSpider(scrapy.Spider):
    name = 'posters'
    allowed_domains = ['chrome.google.com']

    start_urls = ['http://chrome.google.com/webstore/category/extensions']

    def parse(self, response):
        content = response.text
        pattern = re.compile(
            r'(?s)getitemsresponse.*?featured:(?P<mark>\d+@\d+):.*?(?P<featured>\[\"featured\".*?\"(?P=mark)\".*?\])'
        )
        featured_m = re.search(pattern, content)
        featured_json = json.loads(featured_m.group("featured"))

        url_regex = re.compile(r'^https://lh3.googleusercontent.com')
        for w, each_ext in enumerate(featured_json[1]):
            poster = PosterItem()
            poster['ext_id'] = each_ext[0]
            poster['weight'] = w + 1
            poster['image_urls'] = []
            for each_ext_detail in each_ext:
                if re.search(url_regex, str(each_ext_detail)):
                    poster['image_urls'].append(each_ext_detail)
            yield poster