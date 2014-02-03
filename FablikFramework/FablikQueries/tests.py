import unittest,os
import IOTypesStructure as types
from ApplicationImplementation import *

APP = FablikQueriesImplementation()
APP.start_routine({'DEBUG':True, 'FB_DATABASE_STRING':'host=127.0.0.1 user=postgres dbname=fablik_base %s','FB_DATABASE_PASSWORD':'', 'AUDIT_LEVEL':4})
CURSOR_SID = ''
insert_session = "INSERT INTO bf_activesession (session_guid, session_start, user_id) VALUES ('%s',current_timestamp,%i)"
delete_session = "DELETE FROM bf_activesession WHERE session_guid='%s'"
SESSION_ID = 'session_for_test'

APP.database.modify(insert_session % (SESSION_ID, 1))

class TestFablikQueries(unittest.TestCase):
    def test_1_buildQuery(self):
        ret = os.system('psql -U postgres -f CLEAR_TEST_DB.SQL ')
        ret = os.system('psql -U postgres -f TEST_DB.SQL ')
        self.assertEquals(ret, 0, 'Init test database failed')

        (query,desc,iface) = APP.buildQuery('test_sql_query',{})
        print 'QUERY:',query
        self.assertEquals(query, "SELECT id, lastname FROM TEST_USER WHERE ( description is not null ) AND ( lastname like '%%' )", 'Query is invalid')
        self.assertEquals(len(desc), 2, 'Query results is invalid')

        (query,desc,iface) = APP.buildQuery('test_sql_query',{'gAge':20})
        self.assertEquals(query, "SELECT id, lastname FROM TEST_USER WHERE ( age > '20' ) AND ( description is not null ) AND ( lastname like '%%' )", 'Query is invalid')

        (query,desc,iface) = APP.buildQuery('test_sql_query',{'gAge':20, 'workPosition':'student'})
        self.assertEquals(query, "SELECT id, lastname FROM TEST_USER WHERE ( age > '20' ) AND ( work_position = 'student' ) AND ( description is not null ) AND ( lastname like '%%' )", 'Query is invalid')

        (query,desc,iface) = APP.buildQuery('test_sql_query',{'likeLastname':'%enko'})
        self.assertEquals(query, "SELECT id, lastname FROM TEST_USER WHERE ( description is not null ) AND ( lastname like '%enko' )", 'Query is invalid')

        try:
            (query,desc,iface) = APP.buildQuery('test_sql_query',{'raiseError':'bla'})
        except Exception, err:
            pass
        else:
            raise Exception('Exception must be raised')

    def test_2_executeQuery(self):
        req = types.RequestExecuteQuery(session_id=SESSION_ID,sql_query_sid='test_sql_query', filter_list=[types.FilterType(name='lastname', value="'%enko'")])

        resp = APP.executeQuery(req)
        self.assertEquals(resp.ret_code, 0, resp.ret_message)
        self.assertEquals(len(resp.row_list), 2, 'Result rows count must be 2')
        self.assertEquals(len(resp.row_description), 2, 'Result columns count in every row must be 2')


    def test_3_createCursor(self):
        req = types.RequestCreateCursor(session_id=SESSION_ID,sql_query_sid='test_sql_query', filter_list=[types.FilterType(name='lastname', value="'%enko'")])

        resp = APP.createCursor(req)
        self.assertEquals(resp.ret_code, 0, resp.ret_message)
        global CURSOR_SID
        CURSOR_SID = resp.cursor_sid
        print 'created cursor with sid %s'%CURSOR_SID
        self.assertEquals(len(resp.cursor_sid), 33, 'Cursor SID must be 33-character string')
        self.assertEquals(len(resp.row_description), 2, 'Result columns count in every row must be 2')

    def test_7_closeCursor(self):
        req = types.RequestCloseCursor(session_id=SESSION_ID,cursor_sid=CURSOR_SID)

        print 'removing %s cursor'% CURSOR_SID
        resp = APP.closeCursor(req)
        self.assertEquals(resp.ret_code, 0, resp.ret_message)

    def test_6_getCursorData(self):
        req = types.RequestGetCursorData(session_id=SESSION_ID,cursor_sid=CURSOR_SID, fetch_count=2)

        print 'fetch 2 item from %s cursor'% CURSOR_SID
        resp = APP.getCursorData(req)
        self.assertEquals(resp.ret_code, 0, resp.ret_message)
        self.assertEquals(len(resp.row_list), 2, 'Result rows count must be 2')


    def test_9_stopApplication(self):
        APP.database.modify(delete_session % (SESSION_ID))
        APP.stop_routine()
