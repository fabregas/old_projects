import sys
import logging, logging.handlers

def init_logger():
    logger = logging.getLogger('localhost')

    logger.setLevel(logging.INFO)

    log_path = '/dev/log'

    hdlr = logging.handlers.SysLogHandler(address=log_path,
              facility=logging.handlers.SysLogHandler.LOG_DAEMON)
    #formatter = logging.Formatter('%(filename)s: %(levelname)s: %(message)s')
    formatter = logging.Formatter('BLIK %(levelname)s: %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger

logger = init_logger()
