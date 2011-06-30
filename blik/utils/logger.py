from datetime import datetime

class Logger:
    def error(self, message):
        print '[%s] ERROR: %s' % (datetime.now(), message)

    def info(self, message):
        print '[%s] INFO: %s' % (datetime.now(), message)

    def debug(self, message):
        #print '[%s] DEBUG: %s' % (datetime.now(), message)
        pass

logger = Logger()
