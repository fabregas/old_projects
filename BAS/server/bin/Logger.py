import datetime, sys
from sql_queries import sql_insert_log_message
from settings import AS_LOG_FILE

#log levels
LL_INFO         =    0
LL_ERROR        =    2
LL_WARNING      =    4


class Logger:
    def __init__(self, node_name, db_conn, debug):
        self.node_name = node_name
        self.db_conn = db_conn
        self.debug = debug

    def set_debug(self, debug):
        self.debug = debug

    def info(self, message):
        self.log(message, LL_INFO)

    def warning(self, message):
        self.log(message, LL_WARNING)

    def error(self, message):
        if self.debug:
            message += '\n%s TRACEBACK %s\n' %('*'*20, '*'*20)
            message += ''.join(apply(traceback.format_exception, sys.exc_info()))
            message += '*'*50 + '\n'

        self.log(message, LL_ERROR)

    def log(self, message, l_level=LL_INFO):
        dtime = datetime.now()
        try:
            message = message.replace("'", '"')
            self.db_conn.call_func('logMessage',(self.node_name, l_level, message, dtime))(sql_insert_log_message %(self.node_id,dtime,l_level,message))
        except Exception, err:
            sys.stderr.write( "Can't write log message to database! Message: %s\n" % message )
