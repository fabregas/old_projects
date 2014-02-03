
from Database import Database


class CursoredDatabase(Database):
    def fetchFromCursor(self, cursor_sid, sql_query, offset, fetch_count):
        '''
        offset: move count
        fetch_count: fetch count
        '''
        self.start_transaction()
        try:
            self._cursor.close()
            self._cursor = self._conn.cursor(cursor_sid)

            self.execute(sql_query, is_select=False) #is_select=False -> for non fetch execution...

            #scroll cursor to current position
            self._cursor.scroll(offset)

            rows = self._cursor.fetchmany(fetch_count)
            fetched_count = len(rows)

            self._cursor.close()
            self._cursor = self._conn.cursor()

            current_pos = offset + fetched_count
        finally:
            self.end_transaction()

        return rows,current_pos

