# -*- coding: utf-8 -*-
from twisted.enterprise import adbapi
from extensions.items import TagItem, PosterItem, CategoryItem, ExtensionItem
import re, json


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


    def insert_poster(self, tx, item):
        values = (
            item['poster_path'],
            item['weight'],
            item['ext_id'],
        )

        sql = 'insert into posters values (null,%s,%s,%s)'
        tx.execute(sql, values)


    def insert_category(self, tx, item):
        sql = """
            insert into categories (name, code_id, weight, hot_picks) values ("%s", "%s", "%d", '%s')
        """ % (item['name'], item['code_id'], item['weight'], item['hot_picks'])
        # print(sql)
        # 把左边没有{，右边没有}的单引号改成双引号
        exe_sql = re.sub(r"(?<!})'(?!{)", r'\"', sql)
        # print(exe_sql)
        tx.execute(exe_sql)


    def insert_ext(self, tx, item):
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
            item['detail_info'],
            item['category_id'],
            item['update_time'],
        )
        '''
        sql = """
            insert into extensions values (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        '''
        sql = 'insert into extensions values ' \
              '(null,"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",str_to_date("%s", "%%Y年%%m月%%d日"))'
        exe_sql = sql % values
        exe_sql = re.sub(r'\"', r':change:', exe_sql)
        exe_sql = re.sub(r"'", r'\"', exe_sql)
        exe_sql = re.sub(r':change:', r"'", exe_sql)

        with open('sql.txt', 'w') as f:
            f.write(exe_sql)

        tx.execute(exe_sql)