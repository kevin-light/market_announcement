# -*- coding: utf-8 -*-
import scrapy
from urllib.request import urlopen
from pdfminer.pdfinterp import PDFResourceManager,process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open
from scrapy import Spider, Request
import json, re
from market_announcement.loggers import Logger
from market_announcement.items import AnnouncementItem
import datetime
import psycopg2
from market_announcement import settings
import traceback


# log = Logger('market_announcement/logger_daily/annc.log',level='debug')
# pdf_log = Logger('market_announcement/logger_daily/pdf_miner.log',level='debug')

class StocksAnncSpider:
    # name = 'stocks_annc'
    # allowed_domains = ['http://www.cninfo.com.cn/']
    # start_urls = ['http://http://www.cninfo.com.cn/']
    # req_url = "http://www.cninfo.com.cn/search/search.jsp"
    # host_url = 'http://www.cninfo.com.cn'
    # pagesNo = 1
    #
    # # dt = datetime.datetime.now().strftime('%Y-%m-%d')
    # log.logger.debug(dt)
    #
    #
    # custom_settings = {
    #     'DEFAULT_REQUEST_HEADERS': {
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #         'Accept-Language': 'zh-CN,zh;q=0.9',
    #             }
    # }
    #
    # hds = {
    #     'DEFAULT_REQUEST_HEADERS': {
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #         'Accept-Language': 'zh-CN,zh;q=0.9',
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #         'Cache-Control': 'max-age=0',
    #         'Connection': 'keep - alive',
    #         'Content - Length': '149',
    #         'Content - Type': 'application / x - www - form - urlencoded',
    #         'Cookie': 'cninfo_search_record_cookie=%E9%A3%9E%E4%BA%9A%E8%BE%BE%EF%BC%A1; JSESSIONID=017BAA23D4380B6840DAC78072D7CF34',
    #         'Host': 'www.cninfo.com.cn',
    #         'Origin': 'http: // www.cninfo.com.cn',
    #         'Referer': 'http: // www.cninfo.com.cn / search / search.jsp',
    #         'Upgrade - Insecure - Requests': '1',
    #             }}

    #
    # def start_requests(self):
    #
    #     yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp",
    #                              formdata={'orderby': 'date11','startTime': self.dt,
    #                                        'endTime': self.dt,'pageNo': '1'},
    #                              headers=self.hds,callback=self.search_parse)

    dt = '2018-08-14'


    def count_dt(self):
        try:

            conn = psycopg2.connect(
                user=settings.database_user,
                database=settings.database_name,
                password=settings.database_password,
                host=settings.database_host,
                port='5432'
            )
            cur = conn.cursor()
            cur.execute("select count(id) from choice_announcementhistory where annc_now_date=%s", (self.dt,))
            dt_count = cur.fetchone()[0]
            print('2---,',dt_count)
            cur.close()
            conn.close()
        except Exception as e:
            err = traceback.format_exc()
            print('111------',err)
            # log.logger.debug(err)

        return dt_count

    def sql_count(self):
        dt_count = self.count_dt()
        print('333-----,',dt_count)

if __name__ == '__main__':
    sa = StocksAnncSpider()
    sa.sql_count()