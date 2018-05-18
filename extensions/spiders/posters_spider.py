import scrapy
import re
import json

from ..items import PosterItem

"""
###
�ܽ���ɣ�
1����õİ취������ @ ���ţ�����extensions�г��ֵľͺ���
2������ĳЩ�ı���Ҳ�����ˣ���������������ʼ���Ϊ���ų���Щ�������£�
3���������޶���
3.1���ҵ� getitemsresponse ���Ժ�
3.2������ getitemsresponse ������ featured���ͳ������� featured
4�������� featured��һ���� @ ��֪ featured �Ľ����޶�����һ�����ǽ����޶���
��ˣ�������ʽ�ͺ�д�ˡ�

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