import logging, os

class LogManager:
    logger = logging.getLogger('bf_client')

    @classmethod
    def init_log(cls, log_path, log_level=logging.INFO):
        log_file = os.path.join(log_path, 'client.log')

        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)

        cls.logger.addHandler(hdlr)
        cls.logger.setLevel(log_level)

    @classmethod
    def change_log_level(cls, log_level):
        cls.logger.setLevel(log_level)

    @classmethod
    def debug(cls, message):
        cls.logger.debug(message)

    @classmethod
    def info(cls, message):
        cls.logger.info(message)

    @classmethod
    def warning(cls, message):
        cls.logger.warning(message)

    @classmethod
    def error(cls, message):
        cls.logger.error(message)

    @classmethod
    def critical(cls, message):
        cls.logger.critical(message)
