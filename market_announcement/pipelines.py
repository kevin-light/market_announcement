# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class MarketAnnouncementPipeline(object):
#     def process_item(self, item, spider):
#         return item


import psycopg2
from market_announcement import settings
from market_announcement.loggers import Logger

log = Logger('market_announcement/logger_daily/pipelines_con.log',level='debug')


class PgsAnnouncementPipeline(object):

    def process_item(self, item, spider):
        try:
            conn = psycopg2.connect(user=settings.database_user,
                                    database=settings.database_name,
                                    host=settings.database_host,
                                    password=settings.database_password,
                                    port='5432')
            # conn_engine = create_engine(str("postgresql://%s:" + '%s' + '@%s/%s')
            # %(settings.database_user, settings.database_password, settings.database_host,settings.database_name))

            cur = conn.cursor()
            cur.execute("""
            insert into choice_announcementhistory (annc_code,annc_url,annc_title,annc_data,annc_date,annc_now_date)
            values (%s, %s, %s, %s, %s,%s);""",(item['annc_code'],item['annc_url'],item['annc_title'],item['annc_data'],
                                                item['annc_date'],item['annc_now_date']))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.logger.debug(e)
        return item






