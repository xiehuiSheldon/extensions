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
    'extensions.pipelines.MySQLAsyncPipeline': 300,
}

