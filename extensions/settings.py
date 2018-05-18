# -*- coding: utf-8 -*-


BOT_NAME = 'extensions'


SPIDER_MODULES = ['extensions.spiders']
NEWSPIDER_MODULE = 'extensions.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = True


MYSQL_DB_NAME = 'chrome_ext'
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''


ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'extensions.pipelines.MySQLAsyncPipeline': 300,
}

# LOG_FILE = 'tmp/log.txt'

IMAGES_STORE = 'img'
