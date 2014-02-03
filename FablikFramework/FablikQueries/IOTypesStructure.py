import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class FilterType(ClassSerializer):
    name = simple.String
    value = simple.String

class ColumnDescriptionType(ClassSerializer):
    num = simple.Integer
    type = simple.Integer
    name = simple.String

class RowType(ClassSerializer):
    columns = simple.Array(simple.String, 'column', 'columnsArray')

class RequestExecuteQuery(ClassSerializer):
    session_id = simple.String
    sql_query_sid = simple.String
    filter_list = simple.Array(FilterType, 'filter', 'filter_listArray')

class ResponseExecuteQuery(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    row_list = simple.Array(RowType, 'row', 'row_listArray')
    row_description = simple.Array(ColumnDescriptionType, 'column_description', 'row_descriptionArray')

class RequestCreateCursor(ClassSerializer):
    session_id = simple.String
    sql_query_sid = simple.String
    filter_list = simple.Array(FilterType, 'filter', 'filter_listArray')

class ResponseCreateCursor(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    cursor_sid = simple.String
    row_description = simple.Array(ColumnDescriptionType, 'column_description', 'row_descriptionArray')

class RequestCloseCursor(ClassSerializer):
    session_id = simple.String
    cursor_sid = simple.String

class ResponseCloseCursor(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestGetCursorData(ClassSerializer):
    session_id = simple.String
    cursor_sid = simple.String
    offset = simple.Integer
    fetch_count = simple.Integer

class ResponseGetCursorData(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    row_list = simple.Array(RowType, 'row', 'row_listArray')

