
from configManager import Config

class Column(object):
    def __init__(self, c_type, c_name):
        self.type = c_type
        self.name = c_name

class RowData(object):
    def __init__(self):
        self.__num_dict = {}
        self.__named_dict = {}

    def __getitem__(self, idx):
        if type(idx) == int:
            return self.__num_dict[idx]
        else:
            return self.__named_dict[idx]

    def __setitem__(self, idx, item):
        if type(idx) == int:
            self.__num_dict[idx] = item
        else:
            self.__named_dict[idx] = item

    def __getattr__(self, attr):
        if attr in self.__named_dict.keys():
            return self.__named_dict[attr]

        object.__getattr__(self, attr)

    def __repr__(self):
        return str( self.__named_dict )


class Cursor(object):
    def __init__(self, cursor_sid, row_description):
        self.__cursor_sid = cursor_sid
        self.__col_descriptions = {}
        self.closed = False

        for col_desc in row_description.column_description:
            self.__col_descriptions[col_desc.num] = Column(col_desc.type, col_desc.name)

    def get_cursor_sid(self):
        return self.__cursor_sid

    def get_col_descriptions(self):
        return self.__col_descriptions

class Query(object):
    interface = None
    cursors = []

    @classmethod
    def init_query(cls, query_interface):
        cls.interface = query_interface

    @classmethod
    def __perform_data(cls, row_list, col_descriptions):
        data = []

        if not row_list:
            return data

        for row in row_list.row:
            row_data = RowData()
            for i,column in enumerate(row.columns.string):
                #FIXME: append types cast

                if column == None:
                    column = ''
                row_data[i] = column
                row_data[col_descriptions[i].name] = column
            data.append(row_data)

        return data

    @classmethod
    def select(cls, query_sid, **filter_list):
        inputVar = cls.interface.create_variable('RequestExecuteQuery')

        inputVar.session_id = Config.getSessionID()
        inputVar.sql_query_sid = query_sid

        for filter_name in filter_list:
            filter_var = cls.interface.create_variable('filter')
            filter_var.name = filter_name
            filter_var.value = filter_list[filter_name]
            inputVar.filter_list.filter.append( filter_var )

        result = cls.interface.call('executeQuery', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        col_descriptions = {}
        for col_desc in result.row_description.column_description:
            col_descriptions[col_desc.num] = Column(col_desc.type, col_desc.name)

        return cls.__perform_data(result.row_list, col_descriptions)


    @classmethod
    def make_cursor(cls, query_sid, **filter_list):
        inputVar = cls.interface.create_variable('RequestCreateCursor')

        inputVar.session_id = Config.getSessionID()
        inputVar.sql_query_sid = query_sid

        for filter_name in filter_list:
            filter_var = cls.interface.create_variable('filter')
            filter_var.name = filter_name
            filter_var.value = filter_list[filter_name]
            inputVar.filter_list.filter.append( filter_var )

        result = cls.interface.call('createCursor', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        return Cursor(result.cursor_sid, result.row_description)


    @classmethod
    def fetch_cursor(cls, cursor_obj, offset, fetch_count):
        inputVar = cls.interface.create_variable('RequestGetCursorData')

        inputVar.session_id = Config.getSessionID()
        inputVar.cursor_sid = cursor_obj.get_cursor_sid()
        inputVar.offset = offset
        inputVar.fetch_count = fetch_count

        result = cls.interface.call('getCursorData', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        col_descriptions = cursor_obj.get_col_descriptions()

        return cls.__perform_data(result.row_list, col_descriptions)


    @classmethod
    def close_cursor(cls, cursor_obj):
        inputVar = cls.interface.create_variable('RequestCloseCursor')

        inputVar.session_id = Config.getSessionID()
        inputVar.cursor_sid = cursor_obj.get_cursor_sid()

        result = cls.interface.call('closeCursor', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        cursor_obj.closed = True

    @classmethod
    def close_all_cursors(cls):
        for cursor in cls.cursors:
            cls.close_cursor(cursor_sid)
