import IOTypesStructure as IO
from Database import Database
import sql_queries as SQL
import re,uuid
from FablikBaseLib import FablikInterfaces
from FablikBaseLib.FablikBaseLib import FablikBaseRoutines
from FablikBaseLib.FablikErrorCodes import *

class FablikQueriesImplementation:
    def start_routine(self, config):
        self.database = None
        self.base_lib = FablikBaseRoutines(config)

        self.synchronize(config)

    def synchronize(self, config):
        self.debug = config.get('DEBUG', False)
        self.base_lib.synchronize(config)
        self.db_interfaces = {}

        self.database = self.base_lib.get_database_connection()

        self.interface_manager = FablikInterfaces.InterfaceManager(config)

    def stop_routine(self):
        pass

    def loadInterface(self, iface_id):
        db_conn = self.interface_manager.getDatabaseInterfaceByID(iface_id)

        self.db_interfaces[iface_id] = db_conn

    def buildQuery(self, sql_query_sid, filters_map):
        query = self.database.execute(SQL.get_query % sql_query_sid)
        if not query:
            raise Exception('Query with SID %s is not found' % sql_query_sid)

        (qid, interface_id, query, description) = query[0]

        optional_exprs = re.findall('\?(.+)\?', query)
        for op_expr in optional_exprs:
            filters = re.findall('%\(\s*(\w+)\s*\)', op_expr)
            for val in filters:
                if val not in filters_map:
                    query = query.replace('?%s?'%op_expr,'')
                    continue

            query = query.replace('?%s?'%op_expr, op_expr)

        try:
            query = query % filters_map
        except KeyError, key:
            raise Exception('Filter %s is not found. But it should be!' % key)

        return (query, interface_id)


    def executeQuery(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        row_list = []
        row_description = []

        try:
            self.base_lib.auth_by_session(request.session_id)

            filters_map = {}
            if not request.filter_list:
                request.filter_list = []

            for filter_item in request.filter_list:
                filters_map[filter_item.name] = "'%s'" % filter_item.value.replace("'","\\'")

            (query, iface_id) = self.buildQuery(request.sql_query_sid, filters_map)

            if not self.db_interfaces.has_key(iface_id):
                self.loadInterface(iface_id)

            database = self.db_interfaces[iface_id]

            (row_descr, rows) = database.execute(query, is_row_descr=True)

            for row in rows:
                columns = []

                for num,item in enumerate(row):
                    if item is None:
                        item = ''
                    columns.append(str(item))

                row_list.append( IO.RowType(columns=columns) )

            for i,col in enumerate(row_descr):
                row_description.append( IO.ColumnDescriptionType(num=i, type=1, name=col[0]) ) #FIXME: need type mapping
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseExecuteQuery(ret_code=err_code, ret_message=err_message, row_list=row_list, row_description=row_description )


    def createCursor(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        cursor_sid = ''
        row_description = []

        try:
            self.base_lib.auth_by_session(request.session_id)

            filters_map = {}
            if not request.filter_list:
                request.filter_list = []

            for filter_item in request.filter_list:
                filters_map[filter_item.name] = filter_item.value

            (query, iface_id) = self.buildQuery(request.sql_query_sid, filters_map)


            cursor_sid = 'c' + uuid.uuid4().hex
            query = query.replace("'","\\'")
            self.database.modify(SQL.insert_cursor % (request.session_id, cursor_sid, query, iface_id))

            if not self.db_interfaces.has_key(iface_id):
                self.loadInterface(iface_id)

            database = self.db_interfaces[iface_id]

            (row_descr, rows) = database.execute(query+' LIMIT 1', is_row_descr=True)

            for i,col in enumerate(row_descr):
                row_description.append( IO.ColumnDescriptionType(num=i, type=1, name=col[0]) ) #FIXME: need type mapping
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseCreateCursor(ret_code=err_code, ret_message=err_message, cursor_sid=cursor_sid, row_description=row_description )


    def closeCursor(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            self.base_lib.auth_by_session(request.session_id)

            self.database.modify(SQL.remove_cursor % request.cursor_sid)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseCloseCursor(ret_code=err_code, ret_message=err_message )



    def getCursorData(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        row_list = []

        try:
            self.base_lib.auth_by_session(request.session_id)

            cursor_sid = request.cursor_sid
            row_offset = request.offset
            fetch_count = request.fetch_count

            cursor_info = self.database.execute(SQL.get_cursor_info % cursor_sid)

            if not cursor_info:
                raise Exception(FBE_NO_CURSOR, 'Cursor with SID %s is not found' % cursor_sid)

            (sql_statement, iface_id) = cursor_info[0]

            if not self.db_interfaces.has_key(iface_id):
                self.loadInterface(iface_id)

            database = self.db_interfaces[iface_id]

            rows = database.execute(sql_statement + 'OFFSET %i LIMIT %i'% (row_offset,fetch_count))

            for row in rows:
                columns = []

                for num,item in enumerate(row):
                    if item is None:
                        item = ''
                    columns.append(str(item))

                row_list.append( IO.RowType(columns=columns) )
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseGetCursorData(ret_code=err_code, ret_message=err_message, row_list = row_list)

