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
from market_announcement import settings
import traceback
import logging, time


log = Logger('logger_daily/annc.log',level='debug')
pdf_log = Logger('logger_daily/pdf_miner.log',level='debug')

logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)
class StocksAnncSpider(scrapy.Spider):
    name = 'stocks_annc'
    allowed_domains = ['http://www.cninfo.com.cn/']
    start_urls = ['http://http://www.cninfo.com.cn/']
    req_url = "http://www.cninfo.com.cn/search/search.jsp"
    host_url = 'http://www.cninfo.com.cn'
    pagesNo = 1

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
                                 formdata={'orderby': 'date11', 'startTime': settings.startTime,
                                           'endTime': settings.endTime, 'pageNo': str(self.pagesNo)},
                                 headers=self.hds, callback=self.search_parse)

    def search_parse(self, response):

        bodys = response.xpath('//*[@class="da_tbl"]/tbody/tr')

        try:
            for body in bodys:
                code = body.css('.dm::text').extract()
                url = body.css('a::attr(href)').extract()
                title = body.css('a::text').extract()
                dates = body.css('.ggsj::text').extract()
                if len(dates[0]) > 20:
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
                log.logger.debug(self.pagesNo)

                log.logger.debug(title[0])
                log.logger.debug(date)
                item['annc_data'] = annc_data
                item['annc_date'] = date[0]
                item['annc_now_date'] = datetime.date.today()
                # log.logger.debug(item)
                yield item

            pages = response.xpath('//span[@class="sabrosus2"]/span[last()]/a/text()').extract()
            print('----page', pages)
            pg = pages[0]
            if self.pagesNo < int(pages[0]):
                pdf_log.logger.debug(self.pagesNo)
                self.pagesNo += 1
                # print('----pg----', self.pagesNo, type(pg))
                log.logger.debug(self.pagesNo)

                yield scrapy.http.FormRequest("http://www.cninfo.com.cn/search/search.jsp",
                                              formdata={'orderby': 'date11', 'startTime': settings.startTime,
                                                        'endTime': settings.endTime, 'pageNo': str(self.pagesNo)},
                                              callback=self.search_parse, dont_filter=True)

        except Exception as e:
            err = traceback.format_exc()

            pdf_log.logger.debug(err)
            print('page error:', e)

    def readpdf(self, filepdf):

        try:
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, laparams=laparams)
            try:
                process_pdf(rsrcmgr, device, filepdf)
            except Exception:
                time.sleep(10)
            process_pdf(rsrcmgr, device, filepdf)
            device.close()
            content = retstr.getvalue()
            retstr.close()

        except Exception as e:
            content = ""
            err = traceback.format_exc()
            pdf_log.logger.debug(err)


        return content



