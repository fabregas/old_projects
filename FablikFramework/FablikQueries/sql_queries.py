
get_query = "SELECT id, interface_id, query, description FROM BF_SQL_QUERY WHERE sid='%s'"

insert_cursor = "INSERT INTO bf_cursor (session_guid,cursor_sid, sql_statement, interface_id) VALUES ('%s','%s', '%s', %i)"
get_cursor_info = "SELECT sql_statement, interface_id FROM bf_cursor WHERE cursor_sid = '%s'"
remove_cursor = "DELETE FROM bf_cursor WHERE cursor_sid = '%s'"
