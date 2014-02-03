import psycopg2 as psycopg
#import  psycopg
import time
import thread
from Exceptions import Error

#------ exceptions --------------------

class DBError(Error):
    def __init__(self, msg):
        msg = '[Database Error] %s'%msg
        Error.__init__(self, msg)

class DBConnectError(DBError):
    pass


class DBExecuteError(DBError):
    pass

#--------------------------------------


class Database:
    def __init__(self,connect_string):
        self.__conn_string = connect_string

        if not self.__connect():
            raise DBConnectError("Connection faulted...")

        self.__lock = thread.allocate_lock()
        self.__execute_lock = thread.allocate_lock()

    def __del__(self):
        self.__close()

    def __close(self):
        try:
            self.__started = False
            self._cursor.close()
            self._conn.close()
        except psycopg.Error, msg:
            return False

        return True

    def __connect(self):
        try:
            self._conn = psycopg.connect(self.__conn_string)
            self._cursor = self._conn.cursor()
        except psycopg.Error, msg:
            return False

        self.__started = True

        return True

    def get_connection_string(self):
        return self.__conn_string

    def is_transaction(self):
        return self.__lock.locked()

    def start_transaction(self):
        self.__lock.acquire_lock()

    def end_transaction(self, commit=True):
        try:
            if commit:
                self._conn.commit()
        except Exception, err:
            raise Exception(err)
        finally:
            if self.__lock.locked():
                self.__lock.release_lock()

    def __rollback_transaction(self):
        '''
        This method is private because rollback is automatic called while exception occured
        '''
        try:
            self._conn.rollback()
        except Exception, err:
            return False
        finally:
            if self.__lock.locked():
                self.__lock.release_lock()
            if self.__execute_lock.locked():
                self.__execute_lock.release_lock()

        return True

    def close(self):
        self.__close()

    def execute(self, query, is_select=True, is_commit=False, is_row_descr=False):
        '''
        execute SQL <query> thread safety
        '''
        #print query
        self.__execute_lock.acquire_lock()

        try:
            needEnd = False
            if not self.is_transaction():
                self.start_transaction()
                needEnd = True

            if not self.__started and not self.__connect():
                raise Exception('No connection with Database')

            self._cursor.execute(query)

            if is_select:
                ret_list = self._cursor.fetchall()

            if is_row_descr:
                row_descr = self._cursor.description

            if needEnd:
                self.end_transaction(is_commit)
        except psycopg.OperationalError, msg:
            self.__close()
            self.__rollback_transaction()
            raise DBExecuteError("[Database error] %s" %msg)
        except Exception, msg:
            self.__rollback_transaction()
            raise DBExecuteError("[Database error] %s" %msg)
        except:
            self.__rollback_transaction()
            raise DBExecuteError('Database execution unexpected error')


        self.__execute_lock.release_lock() #release this lock in __rollback_transaction if fault

        if is_select:
            if is_row_descr:
                return (row_descr, ret_list)
            return ret_list

    def modify(self, query):
        '''
        execute modify SQL <query> (INSERT, UPDATE, DELETE, etc.)
        '''
        self.execute(query, is_select=False, is_commit=True)





################################################################################################


'''
#first usage
try:
    db = Database('host=127.0.0.1 user=postgres dbname=bas_db')

    for i in xrange(10):
        thread.start_new_thread(do_select, (db,i))

    import time
    time.sleep(1)
    try:
        ret = db.execute("select fail from bas_application")
    except Exception, err:
        print err

    while ITER != 10:
        time.sleep(1)

    print 'RET'
    db.close()
except Exception, msg:
    print msg


#second usage
try:
    db = Database('host=127.0.0.1 user=postgres dbname=bas_db')

    db.start_transaction()

    db.modify("delete from bas_application where id=1") 
    #some other operations...

    db.end_transaction()

    db.close()
except Exception, msg:
    print msg


'''
