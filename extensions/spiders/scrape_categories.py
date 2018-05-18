import re
import requests
from scrapy.selector import Selector


class ScrapeCategories:
    def __init__(self, url):
        text = self.getHtmlText(url)
        self.categories = self.parseText(text)

    def getHtmlText(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        }
        try:
            r = requests.get(url, timeout=30, headers=headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            return ""  # 现在出现问题，直接返回空串

    def parseText(self, text):
        categories = []
        selector = Selector(text=text)
        all_content = selector.xpath('//script[@id="cws-model-data"]/text()').extract()[0]
        # 获取插件类型数据
        w = 0
        cat_line_regex = re.compile(r'\[\"(ext/[^\"]+?)\",\"([^\"]+?)\".+\n,(.+)\n')
        for cat_iter in re.finditer(cat_line_regex, all_content):
            category = {}
            ext_code_id = cat_iter.group(1)
            category['ext_code_id'] = ext_code_id
            code_id = re.split(r'/', ext_code_id)[1]
            category['code_id'] = code_id
            category['no_number_code_id'] = re.search(r'\d+-(.+)', code_id).group(1)
            category['name'] = cat_iter.group(2)
            second_line = cat_iter.group(3)
            w += 1
            category['weight'] = w
            by_google_regex = re.compile(r'by-google')
            if re.search(by_google_regex, ext_code_id):
                category['second_line'] = []
            else:
                second_line = re.sub(r',null', r'', second_line)
                second_line = eval(second_line)
                category['second_line'] = second_line
            categories.append(category)
        return categories


if __name__ == '__main__':
    cat = ScrapeCategories('https://chrome.google.com/webstore/category/extensions')
    import json
    print(json.dumps(cat.categories))