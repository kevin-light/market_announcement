import logging
from logging import handlers


class Logger(object):

    level_realtion = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning':logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self,filename,level='info',when='midnight',interval=90,backCount=3,fmt='%(asctime)s-%(pathname)s[lineno)d]-%(levelname)s:%(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_realtion.get(level))

        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,interval=interval,backupCount=backCount,encoding='utf-8')

        th.setFormatter(format_str)
        self.logger.addHandler(th)
