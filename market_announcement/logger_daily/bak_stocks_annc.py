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
from scrapy.selector import Selector
from market_announcement.items import AnnouncementItem
import datetime
from market_announcement import settings



class StocksAnncSpider(scrapy.Spider):
    name = 'stocks_annc'
    allowed_domains = ['http://www.cninfo.com.cn/']
    start_urls = ['http://http://www.cninfo.com.cn/']
    req_url = "http://www.cninfo.com.cn/search/search.jsp"
    host_url = 'http://www.cninfo.com.cn'
    pagesNo = 1
    # pg = 1
    # for i in range(0, pg):
    #     pagesNo.append(str(i + 1))

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Accept-Language': 'en',
        }
    }


    # def make_requests_from_url(self):
    #
    #     yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp", formdata={'orderby': 'date11',
    #                              'startTime': '2018-07-13','endTime': '2018-07-13','pageNo': '1'},callback=self.pages_parse)
    #
    # def pages_parse(self,response):
    #
    #     pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
    #     pg = pages[0]
    #     print('-----pag-------',self.pg)
    #     for i in range(0, pg):
    #         self.pagesNo.append(str(i + 1))
        # for i in range(0,pg):
        # self.pagesNo.append(str(i+1))

    # if self.pagesNo:
    #     self.start_requests()
    #     print('------i------', self.pagesNo)
    #     pn = str(i+1)
    #     print('------',pn,pg)
    # return [scrapy.FormRequest.from_response(response,url="http://www.cninfo.com.cn/search/search.jsp",  formdata={'orderby': 'date11',
    #                     'startTime': '2018-07-13', 'endTime':'2018-07-13','pageNo':pn}, callback=self.search_parse,dont_filter=True)]

    def start_requests(self):

        yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp", formdata={'orderby': 'date11',
                                                                                         'startTime': '2018-07-16',
                                                                                         'endTime': '2018-07-16',
                                                                                         'pageNo': '1'},
                                 callback=self.search_parse)


        # if self.pagesNo:
        #     for i in self.pagesNo:
        #         print(i)
        #
        #         yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp",  formdata={'orderby': 'date11',
        #                             'startTime': '2018-07-13', 'endTime':'2018-07-13','pageNo':'1'}, callback=self.pages_parse)
        # else:
        #     pass
            # yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp", formdata={'orderby': 'date11',
            #                          'startTime': '2018-07-13','endTime': '2018-07-13','pageNo': '1'},callback=self.search_parse)

    # def pages_parse(self,response):
    #
    #     pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
    #     pg = pages[0]
    #     print('-----pag-------',pg)
    #     for i in range(0, int(pg)):
    #         self.pagesNo.append(str(i + 1))
    #     for pn in self.pagesNo:
    #         yield scrapy.http.FormRequest("http://www.cninfo.com.cn/search/search.jsp", formdata={'orderby': 'date11',
    #                                  'startTime': '2018-07-13','endTime': '2018-07-13','pageNo': pn},callback=self.search_parse)



    # def start_requests(self):
    #
    #
    #
    #     yield scrapy.FormRequest("http://www.cninfo.com.cn/search/search.jsp", headers=self.custom_settings, formdata={'orderby': 'date11',
    #                         'startTime': '2018-07-13', 'endTime':'2018-07-13','pageNo':'1'}, callback=self.search_parse)

    # def pages_parse(self,response):
    #
    #     pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
    #     pg = int(pages[0])
    #     for i in range(0,pg):
        #     self.pagesNo.append(str(i+1))
        #
        # if self.pagesNo:
        #     self.start_requests()
        #     print('------i------', self.pagesNo)
        #     pn = str(i+1)
        #     print('------',pn,pg)
            # return [scrapy.FormRequest.from_response(response,url="http://www.cninfo.com.cn/search/search.jsp",  formdata={'orderby': 'date11',
            #                     'startTime': '2018-07-13', 'endTime':'2018-07-13','pageNo':pn}, callback=self.search_parse,dont_filter=True)]


    def search_parse(self, response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')

        for body in bodys:
            print('---22---------', body)
            # code = body.xpath('//tr/td[@class="dm"]/text()').extract()
            code = body.css('.dm::text').extract()
            url = body.css('a::attr(href)').extract()
            title = body.css('a::text').extract()
            date = body.css('.ggsj::text').re(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})")
            # datetime = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", date[0])
            # annc_url = response.urljoin(url)
            annc_url = self.host_url + url[0]
            # print('-----7777------',annc_url)
            file_data = urlopen(annc_url)
            annc_title =self.readpdf(file_data)
            # print('-----7777------',annc_title)
            annc_title = re.sub("\n|\t|\s|\r","",annc_title)
            annc_now_date = datetime.date.today().strftime("Y-%m-%d")

            item = AnnouncementItem()

            # print('------111-------\n',code,annc_url,title,date)
            item['annc_code'] = code[0]
            item['annc_url'] = url[0]
            item['annc_title'] = title[0]
            item['annc_data'] = annc_title
            item['annc_date'] = date[0]
            item['annc_now_date'] = datetime.date.today()

            yield item

        pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
        pg = pages[0]
        if self.pagesNo < int(pages[0]):
            self.pagesNo += 1
            print('----pg----', self.pagesNo, type(pg))

            yield scrapy.http.FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                          formdata={'orderby': 'date11','startTime': '2018-07-16',
                                                    'endTime': '2018-07-16', 'pageNo': str(self.pagesNo)},
                                          callback=self.search_parse, dont_filter=True)
        else:
            pass



    def readpdf(self,filepdf):

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        process_pdf(rsrcmgr, device, filepdf)
        device.close()
        content = retstr.getvalue()
        retstr.close()

        return content