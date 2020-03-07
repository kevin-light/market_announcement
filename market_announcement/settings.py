# -*- coding: utf-8 -*-
from  scrapy.pipelines.files import FilesPipeline
import scrapy
# Scrapy settings for market_announcement project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'market_announcement'

SPIDER_MODULES = ['market_announcement.spiders']
NEWSPIDER_MODULE = 'market_announcement.spiders'

startTime = "2018-08-01"
endTime = '2018-08-01'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'market_announcement (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_ENABLED=False    #关闭日志打印
LOG_LEVEL = 'ERROR'      #设置打印日志level



# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'market_announcement.middlewares.MarketAnnouncementSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'market_announcement.middlewares.MarketAnnouncementDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'market_announcement.pipelines.MarketAnnouncementPipeline': 300,
   'market_announcement.pipelines.PgsAnnouncementPipeline': 300,
   #  'scrapy.pipelines.files.FilesPipeline' : 1,
   #  'market_announcement.pipelines.MyFilePipeline': 1
}
# ITEM_PIPELINES = {'scrapy.pipelines.files.FilesPipeline': 1}


FILES_STORE = '/Users/san/Documents/company/crawler/market_announcement/filepdf/'

# 90 days of delay for files expiration
FILES_EXPIRES = 90


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# database_name = 'pgsdb1'
# database_user = 'alvin'
# database_password = '654321'

# database_name = 'db_dev_django'
# database_user = 'db_user'
# database_password = 'test1234'

database_name = 'pgsdb01'
database_user = 'kevinpgs'
database_password = ''

database_host = 'localhost'

