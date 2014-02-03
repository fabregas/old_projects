
from Database import Database
from FablikErrorCodes import FBE_INVALID_DB_CONNECT

class DBConnection:
    connection = None

    @classmethod
    def create_connection(cls, conn_string, conn_class=Database):
        '''
        conn_string - connection parameters
        conn_class - thread-safe DB connection class (must close connection while destroing)
        '''

        if cls.connection is not None:
            if cls.connection.get_connection_string() != conn_string:
                return cls.reconnect(conn_string, conn_class)

            return cls.connection

        return cls.reconnect(conn_string, conn_class)


    @classmethod
    def reconnect(cls, conn_string, conn_class=Database):
        if cls.connection is not None:
            cls.connection.stop()

        try:
            cls.connection = conn_class(conn_string)
        except Exception, err:
            raise Exception (FBE_INVALID_DB_CONNECT, 'Database connection is not esteblished! Details: %s'%err)

        return cls.connection


    @classmethod
    def get_connection(cls):
        if cls.connection is None:
            raise Exception (FBE_INVALID_DB_CONNECT, 'No database connection! Call create_connection method for it esteblish!')

        return cls.connection
