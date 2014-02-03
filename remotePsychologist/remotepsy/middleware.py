from django.middleware.common import CommonMiddleware
import logging

def init_logger():
    logger = logging.getLogger('remotepsy.access')
    hdlr = logging.FileHandler('/var/log/access.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)
    #logger.setLevel(logging.DEBUG)

    return logger

logger = init_logger()

class RequestLogMiddleware(CommonMiddleware):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        if response.status_code < 400:
            logger.info('%s - %s - %s'%(response.status_code, request.META['REMOTE_ADDR'], request.get_full_path()))
        else:
            logger.error('%s - %s - %s'%(response.status_code, request.META['REMOTE_ADDR'], request.get_full_path()))
    
        return response
