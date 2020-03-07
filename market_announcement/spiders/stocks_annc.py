# -*- coding: utf-8 -*-
import scrapy
from urllib.request import urlopen
from pdfminer.pdfinterp import PDFResourceManager,process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from scrapy.http import FormRequest
from io import StringIO
from io import open
from scrapy import Spider, Request
import json, re
from market_announcement.loggers import Logger
from market_announcement.items import AnnouncementItem
import datetime,time
import psycopg2
from market_announcement import settings
import traceback


log = Logger('market_announcement/logger_daily/annc.log',level='debug')
pdf_log = Logger('market_announcement/logger_daily/pdf_miner.log',level='debug')

class StocksAnncSpider(scrapy.Spider):
    name = 'stocks_annc'
    allowed_domains = ['http://www.cninfo.com.cn/']
    start_urls = ['http://http://www.cninfo.com.cn/']
    req_url = "http://www.cninfo.com.cn/search/search.jsp"
    host_url = 'http://www.cninfo.com.cn'
    pagesNo = 1
    pages = 0
    dt_count = 0


    # dt = datetime.datetime.now().strftime('%Y-%m-%d')
    dt = '2018-08-06'
    log.logger.debug(dt)


    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
                }
    }

    hds = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep - alive',
            'Content - Length': '149',
            'Content - Type': 'application / x - www - form - urlencoded',
            'Cookie': 'cninfo_search_record_cookie=%E9%A3%9E%E4%BA%9A%E8%BE%BE%EF%BC%A1; JSESSIONID=017BAA23D4380B6840DAC78072D7CF34',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http: // www.cninfo.com.cn',
            'Referer': 'http: // www.cninfo.com.cn / search / search.jsp',
            'Upgrade - Insecure - Requests': '1',
                }}


    def start_requests(self):

        yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                 formdata={'orderby': 'date11','startTime': self.dt,
                                           'endTime': self.dt,'pageNo': '1'},
                                 headers=self.hds,callback=self.search_parse)

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
            log.logger.debug(err)

        return dt_count

    def search_parse(self, response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')
        self.pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()

        try:

            self.dt_count = self.count_dt()
            print('333---,', self.dt_count)
            if self.dt_count == 0:
                for body in bodys:
                    code = body.css('.dm::text').extract()
                    url = body.css('a::attr(href)').extract()
                    title = body.css('a::text').extract()
                    date = body.css('.ggsj::text').extract()
                    if len(date[0]) > 20:
                        date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                    else:
                        date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")

                    annc_url = self.host_url + url[0]
                    log.logger.debug(annc_url)
                    try:
                        file_data = urlopen(annc_url)
                    except Exception:
                        time.sleep(10)
                        file_data = urlopen(annc_url)

                    annc_data = self.readpdf(file_data)
                    annc_data = re.sub("\n|\t|\s|\r","",annc_data)
                    annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                    item = AnnouncementItem()
                    item['annc_code'] = code[0]
                    item['annc_url'] = url[0]
                    item['annc_title'] = title[0]
                    item['annc_data'] = annc_data
                    item['annc_date'] = date[0]
                    item['annc_now_date'] = datetime.date.today()
                    log.logger.debug(item)
                    yield item

                # pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
                # pg = pages[0]
                if self.pagesNo < int(self.pages[0]):
                    log.logger.debug(self.pagesNo)
                    self.pagesNo += 1
                    # print('----pg----', self.pagesNo, type(pg))
                    log.logger.debug(self.pagesNo)

                    yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                                  formdata={'orderby': 'date11','startTime': self.dt,
                                                            'endTime': self.dt, 'pageNo': str(self.pagesNo)},
                                                  callback=self.first_parse, dont_filter=True)
                    # self.pagesNo += 1

            else:

                sp_count = response.xpath('//span[@class="count"]/text()').extract()
                sp_count = int(re.sub(r'\D', "", sp_count[0]))

                difference_count = sp_count - self.dt_count

                whole_page = difference_count//30
                try:
                    while self.pagesNo < whole_page:
                        pdf_log.logger.debug(self.pagesNo)
                        self.pagesNo += 1

                        yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                                      formdata={'orderby': 'date11', 'startTime': self.dt,
                                                                'endTime': self.dt,
                                                                'pageNo': str(self.pagesNo)},
                                                      callback=self.whole_pages, dont_filter=True)
                except Exception as e:
                    print(e)
                    err = traceback.format_exc()
                    pdf_log.logger.debug(err)
                finally:

                # if whole_page == 0:
                #     yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                #                       formdata={'orderby': 'date11', 'startTime': self.dt,
                #                                 'endTime': self.dt,
                #                                 'pageNo': str(whole_page + 1)},
                #                       callback=self.remainder_parse, dont_filter=True)
                #
                # else:

                    yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                                  formdata={'orderby': 'date11', 'startTime': self.dt,
                                                            'endTime': self.dt,
                                                            'pageNo': str(whole_page+1)},
                                                  callback=self.remainder_parse, dont_filter=True)


                    # for body in bodys:
                    #     code = body.css('.dm::text').extract()
                    #     url = body.css('a::attr(href)').extract()
                    #     title = body.css('a::text').extract()
                    #     date = body.css('.ggsj::text').extract()
                    #     if len(date[0]) > 20:
                    #         date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                    #     else:
                    #         date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")
                    #
                    #     annc_url = self.host_url + url[0]
                    #     file_data = urlopen(annc_url)
                    #     annc_title = self.readpdf(file_data)
                    #     annc_data = re.sub("\n|\t|\s|\r", "", annc_title)
                    #     annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                    #     item = AnnouncementItem()
                    #     item['annc_code'] = code[0]
                    #     item['annc_url'] = url[0]
                    #     item['annc_title'] = title[0]
                    #     item['annc_data'] = annc_data
                    #     item['annc_date'] = date[0]
                    #     item['annc_now_date'] = datetime.date.today()
                    #     log.logger.debug(item)
                    #     yield item
                    #
                    # # pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
                    # # pg = pages[0]
                    # if self.pagesNo < int(pages[0]):
                    #     self.pagesNo += 1
                    #     # print('----pg----', self.pagesNo, type(pg))
                    #     log.logger.debug(self.pagesNo)
                    #
                    #     yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                    #                                   formdata={'orderby': 'date11', 'startTime': '2018-07-16',
                    #                                             'endTime': '2018-07-16',
                    #                                             'pageNo': str(whole_page)},
                    #                                   callback=self.search_parse, dont_filter=True)
                    #
                    # remainder = difference_count%30
                    # if remainder != 0:
                    #     if self.pagesNo < int(pages[0]):
                    #         self.pagesNo = 1
                    #         # print('----pg----', self.pagesNo, type(pg))
                    #         log.logger.debug(self.pagesNo)
                    #
                    #         yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                    #                                       formdata={'orderby': 'date11', 'startTime': '2018-07-16',
                    #                                                 'endTime': '2018-07-16',
                    #                                                 'pageNo': str(whole_page+1)},
                    #                                       callback=self.search_parse, dont_filter=True)
                    #
                    #     whole_page = difference_count // 30
                    #     for body in bodys:
                    #         code = body.css('.dm::text').extract()
                    #         url = body.css('a::attr(href)').extract()
                    #         title = body.css('a::text').extract()
                    #         date = body.css('.ggsj::text').extract()
                    #         if len(date[0]) > 20:
                    #             date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                    #         else:
                    #             date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")
                    #
                    #         annc_url = self.host_url + url[0]
                    #         file_data = urlopen(annc_url)
                    #         annc_title = self.readpdf(file_data)
                    #         annc_data = re.sub("\n|\t|\s|\r", "", annc_title)
                    #         annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                    #         item = AnnouncementItem()
                    #         item['annc_code'] = code[0]
                    #         item['annc_url'] = url[0]
                    #         item['annc_title'] = title[0]
                    #         item['annc_data'] = annc_data
                    #         item['annc_date'] = date[0]
                    #         item['annc_now_date'] = datetime.date.today()
                    #         log.logger.debug(item)
                    #         yield item

                        # pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
                        # pg = pages[0]
                        # if self.pagesNo < int(pages[0]):
                        #     self.pagesNo += 1
                        #     # print('----pg----', self.pagesNo, type(pg))
                        #     log.logger.debug(self.pagesNo)
                        #
                        #     yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                        #                                   formdata={'orderby': 'date11', 'startTime': '2018-07-16',
                        #                                             'endTime': '2018-07-16',
                        #                                             'pageNo': str(whole_page+1)},
                        #                                   callback=self.search_parse, dont_filter=True)


        except Exception:
            err = traceback.format_exc()
            print(err)
            log.logger.debug(err)


    def first_parse(self, response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')
        # pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()

        try:

            # dt_count = self.count_dt()
            # print('3---,', dt_count)
            for body in bodys:
                code = body.css('.dm::text').extract()
                url = body.css('a::attr(href)').extract()
                title = body.css('a::text').extract()
                date = body.css('.ggsj::text').extract()
                if len(date[0]) > 20:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                else:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")

                annc_url = self.host_url + url[0]
                log.logger.debug(annc_url)
                try:
                    file_data = urlopen(annc_url)
                except Exception:
                    time.sleep(10)
                    file_data = urlopen(annc_url)

                annc_data = self.readpdf(file_data)
                annc_data = re.sub("\n|\t|\s|\r", "", annc_data)
                annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                item = AnnouncementItem()
                item['annc_code'] = code[0]
                item['annc_url'] = url[0]
                item['annc_title'] = title[0]
                item['annc_data'] = annc_data
                item['annc_date'] = date[0]
                item['annc_now_date'] = datetime.date.today()
                log.logger.debug(item)
                yield item

                # pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
                # pg = pages[0]
                while self.pagesNo < int(self.pages[0]):
                    log.logger.debug(self.pagesNo)
                    self.pagesNo += 1
                    # print('----pg----', self.pagesNo, type(pg))
                    pdf_log.logger.debug(self.pagesNo)

                    yield FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                                  formdata={'orderby': 'date11','startTime': self.dt,
                                                            'endTime': self.dt, 'pageNo': str(self.pagesNo)},
                                                  callback=self.first_parse, dont_filter=True)
        except Exception as e:
            print(e)
            err = traceback.format_exc()
            log.logger.debug(err)



    def remainder_parse(self,response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')
        # dt_count = self.count_dt()
        sp_count = response.xpath('//span[@class="count"]/text()').extract()
        sp_count = int(re.sub(r'\D', "", sp_count[0]))
        difference_count = sp_count - self.dt_count
        if difference_count <= 30:
            for body in bodys[:difference_count]:
                code = body.css('.dm::text').extract()
                url = body.css('a::attr(href)').extract()
                title = body.css('a::text').extract()
                date = body.css('.ggsj::text').extract()
                if len(date[0]) > 20:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                else:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")

                annc_url = self.host_url + url[0]
                log.logger.debug(annc_url)
                try:
                    file_data = urlopen(annc_url)
                except Exception:
                    time.sleep(10)
                    file_data = urlopen(annc_url)

                annc_data = self.readpdf(file_data)
                annc_data = re.sub("\n|\t|\s|\r", "", annc_data)
                annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                item = AnnouncementItem()
                item['annc_code'] = code[0]
                item['annc_url'] = url[0]
                item['annc_title'] = title[0]
                item['annc_data'] = annc_data
                item['annc_date'] = date[0]
                item['annc_now_date'] = datetime.date.today()
                log.logger.debug(item)
                yield item

    def whole_pages(self,response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')

        try:
            #
            # dt_count = self.count_dt()
            # print('333---,', dt_count)
            # if dt_count == 0:
            for body in bodys:
                code = body.css('.dm::text').extract()
                url = body.css('a::attr(href)').extract()
                title = body.css('a::text').extract()
                date = body.css('.ggsj::text').extract()
                if len(date[0]) > 20:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
                else:
                    date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")
                annc_url = self.host_url + url[0]
                log.logger.debug(annc_url)
                try:
                    file_data = urlopen(annc_url)
                except Exception:
                    time.sleep(10)
                    file_data = urlopen(annc_url)

                annc_data = self.readpdf(file_data)
                annc_data = re.sub("\n|\t|\s|\r", "", annc_data)
                annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
                item = AnnouncementItem()
                item['annc_code'] = code[0]
                item['annc_url'] = url[0]
                item['annc_title'] = title[0]
                item['annc_data'] = annc_data
                item['annc_date'] = date[0]
                item['annc_now_date'] = datetime.date.today()
                # log.logger.debug(item)
                yield item
        except Exception as e:
            err = traceback.format_exc()
            pdf_log.logger.debug(err)


    # def remainder_pages(self,response):
    #
    #     bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')
    #     pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
    #     dt_count = self.count_dt()
    #     sp_count = response.xpath('//span[@class="count"]/text()').extract()
    #     difference_count = sp_count - dt_count
    #     if difference_count <= 30:
    #         for body in bodys[:difference_count]:
    #             code = body.css('.dm::text').extract()
    #             url = body.css('a::attr(href)').extract()
    #             title = body.css('a::text').extract()
    #             date = body.css('.ggsj::text').extract()
    #             if len(date[0]) > 20:
    #                 date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
    #             else:
    #                 date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2})")
    #
    #             annc_url = self.host_url + url[0]
    #             file_data = urlopen(annc_url)
    #             annc_title = self.readpdf(file_data)
    #             annc_data = re.sub("\n|\t|\s|\r", "", annc_title)
    #             annc_now_date = datetime.date.today().strftime("%Y-%m-%d")
    #             item = AnnouncementItem()
    #             item['annc_code'] = code[0]
    #             item['annc_url'] = url[0]
    #             item['annc_title'] = title[0]
    #             item['annc_data'] = annc_data
    #             item['annc_date'] = date[0]
    #             item['annc_now_date'] = datetime.date.today()
    #             log.logger.debug(item)
    #             yield item


    def readpdf(self,filepdf):

        try:
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, laparams=laparams)
            try:
                process_pdf(rsrcmgr, device, filepdf)
            except Exception:
                time.sleep(10)
            device.close()
            content = retstr.getvalue()
            retstr.close()
        except Exception as e:
            content = ""
            pdf_log.logger.debug(e)
        return content