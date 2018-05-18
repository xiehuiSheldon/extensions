# -*- coding: utf-8 -*-
import re
import json

from twisted.enterprise import adbapi

from .items import TagItem, PosterItem, CategoryItem, ExtensionItem, TagsExtensionsItem


# Twisted中adbapi连接池访问MySQL数据库
class MySQLAsyncPipeline:
    def open_spider(self, spider):
        # 这里的和配置文件的区别是，配置文件的是真正的，这里的是默认的
        db = spider.settings.get('MYSQL_DB_NAME', 'scrapy_default')
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', 'root')

        self.dbpool = adbapi.ConnectionPool('pymysql', host=host, db=db, port=port,
                                            user=user, passwd=passwd, charset='utf8')

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        if isinstance(item, TagItem):
            self.dbpool.runInteraction(self.insert_tag, item)
        elif isinstance(item, PosterItem):
            self.dbpool.runInteraction(self.insert_poster, item)
        elif isinstance(item, CategoryItem):
            self.dbpool.runInteraction(self.insert_category, item)
        elif isinstance(item, ExtensionItem):
            self.dbpool.runInteraction(self.insert_ext, item)
        elif isinstance(item, TagsExtensionsItem):
            self.dbpool.runInteraction(self.insert_tags_exts, item)
        return item

    def insert_tag(self, tx, item):
        values = (
            item['name'],
            item['code_id'],
            item['descript'],
            item['weight'],
        )
        sql = 'insert into tags values (null,%s,%s,%s,%s)'
        tx.execute(sql, values)

    def insert_tags_exts(self, tx, item):
        values = (item['tag_id'], item['ext_code_id'])
        sql = 'insert into tags_extensions values (%s, %s)'
        tx.execute(sql, values)

    def insert_poster(self, tx, item):
        values = (
            item['weight'],
            item['ext_code_id'],
            json.dumps(item['image_urls']),
            json.dumps(item['images']),  # 当没有汉字时，无论list，还是jsonList，直接转成json就可以存入。
        )
        sql = 'insert into posters values (null,"%s","%s",\'%s\',\'%s\')'
        exe_sql = sql % values
        tx.execute(exe_sql)

    def insert_category(self, tx, item):
        if 'hot_picks' in item:
            hot_picks = json.dumps(item['hot_picks'], ensure_ascii=False)
            hot_picks = re.sub(r"'", r"\'", hot_picks)
            values = (
                item['name'],
                item['code_id'],
                item['weight'],
                hot_picks,
            )
            sql = 'insert into categories values (null,"%s","%s","%s",\'%s\')'
            exe_sql = sql % values
            tx.execute(exe_sql)
        else:
            values = (item['name'], item['code_id'], item['weight'])
            sql = 'insert into categories values (null,"%s","%s","%s",null)'
            tx.execute(sql, values)

    def insert_ext(self, tx, item):
        detail_info = json.dumps(item['detail_info'], ensure_ascii=False)
        detail_info = re.sub(r"'", r"\'", detail_info)
        values = (
            item['code_id'],
            item['name'],
            item['short_intro'],
            item['thumbnail_path'],
            item['rank'],
            item['download_count'],
            item['free'],
            item['top'],
            item['related_ext'],
            # json.dumps(item['detail_info']),
            detail_info,
            item['category_id'],
            item['update_time'],
        )
        sql = 'insert into extensions values ' \
              '(null,"%s","%s","%s","%s","%s","%s","%s","%s","%s",\'%s\',"%s",str_to_date("%s", "%%Y年%%m月%%d日"))'
        exe_sql = sql % values
        tx.execute(exe_sql)