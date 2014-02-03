from PyQt4.QtGui import QTableWidgetItem, QTableWidget,QTreeWidgetItem
from PyQt4 import QtCore,QtGui
from queryInterface import Query

DEFAULT_FETCH = 50

class QueryTableWraper:
    def __init__(self, query_sid, **filters):
        self._query_sid = query_sid

        self._filters = {}
        for key in filters:
            self._filters[key] = filters[key]

    def wrap(self, tableWidget, fieldsMap, hiddenFields=[]):
        self._tableWidget = tableWidget
        self._fields_map = fieldsMap
        self._hidden_fields = hiddenFields
        self._fields = {}

        visible_count = len(fieldsMap)
        hidden_count = len(hiddenFields)
        for i, item in enumerate(self._fields_map):
            self._fields[item] = i

        for i, item in enumerate(self._hidden_fields):
            self._fields[item] = visible_count + i

        self._tableWidget.setColumnCount(visible_count + hidden_count)
        for i in range(visible_count, visible_count + hidden_count):
            self._tableWidget.setColumnHidden(i, True)

        self._on_table_show()

    def getItem(self, row_num, field_sid):
        col_id = self._fields.get(field_sid, None)

        if col_id is None:
            raise Exception('Field sid "%s" is not found!' % field_sid)

        return self._tableWidget.item(row_num, col_id).text()


    def _on_table_show(self):
        rowCount = self._tableWidget.rowCount()

        try:
            data = Query.select(self._query_sid, **self._filters)
        except Exception, err:
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self._tableWidget.tr('ERROR'), unicode(err), QtGui.QMessageBox.Ok, self._tableWidget).exec_()
            return

        self._tableWidget.setRowCount( rowCount + len(data) )

        for i, item in enumerate(data):
            for j, row_name in enumerate(self._fields_map):
                self._tableWidget.setItem(rowCount+i, j, QTableWidgetItem(str(item[row_name])))

            for key in self._hidden_fields:
                self._tableWidget.setItem(rowCount+i, self._fields[key], QTableWidgetItem(str(item[key])))




class TreeWraper (QueryTableWraper):
    def wrap(self, tableWidget, id_field, parent_id_field, fieldsMap, hiddenFields=[]):
        self._id_field = id_field
        self._parent_sid = parent_id_field

        QueryTableWraper.wrap(self, tableWidget, fieldsMap, hiddenFields)


    def getItem(self, row_num, field_sid):
        raise Exception ('For TreeWidget getItem is not implementes. It is not a bug, it is feature')

    def getCurrentItem(self, field_sid):
        col_id = self._fields.get(field_sid, None)

        if col_id is None:
            raise Exception('Field sid "%s" is not found!' % field_sid)

        curr = self._tableWidget.currentItem()
        if not curr:
            return
        return curr.text(col_id)

    def getCurrentItemLine(self):
        cur_item = self._tableWidget.currentItem()
        if not cur_item:
            return

        ret_map = {}
        for (key,value) in self._fields.items():
            ret_map[key] = cur_item.text(value)

        return ret_map

    def _on_table_show(self):
        self._tableWidget.clear()
        try:
            data = Query.select(self._query_sid, **self._filters)
        except Exception, err:
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self._tableWidget.tr('ERROR'), unicode(err), QtGui.QMessageBox.Ok, self._tableWidget).exec_()
            return

        items_map = {}
        hierarchy = {}
        top_items = []
        for i, item in enumerate(data):
            new_item = []

            for j, row_name in enumerate(self._fields_map):
                new_item.append( str(item[row_name]) )

            for key in self._hidden_fields:
                new_item.append( str(item[key]) )

            oid = item[self._id_field]
            parent_id = item[self._parent_sid]

            if parent_id is not '':
                if not hierarchy.has_key(parent_id):
                    hierarchy[parent_id] = [oid]
                else:
                    hierarchy[parent_id].append(oid)
            else:
                top_items.append(oid)

            items_map[item[self._id_field]] = new_item


        def link_subitems(item_id, parent_item):
            new_item = QTreeWidgetItem(parent_item, items_map[item_id])
            if parent_item != self._tableWidget:
                parent_item.addChild( new_item )

            children_ids = hierarchy.get(item_id,[])
            for child_id in children_ids:
                link_subitems(child_id, new_item)

            if parent_item == self._tableWidget:
                self._tableWidget.insertTopLevelItem(0, new_item)

        for item_id in top_items:
            link_subitems(item_id, self._tableWidget)




class CursorTableWraper(QueryTableWraper):
    def __init__(self, query_sid, **filters):
        QueryTableWraper.__init__(self, query_sid, **filters)
        self.__offset = 0

        try:
            self.__cursor = Query.make_cursor(query_sid, **filters)
        except Exception, err:
            print err #TODO: show message box with error message

    def wrap(self, tableWidget, fieldsMap, hiddenFields=[], fetchCount=DEFAULT_FETCH):
        self.__count = fetchCount

        scrollBar = tableWidget.verticalScrollBar()
        scrollBar.sliderReleased().connect( self.__on_table_scroll )
        tableWidget.wheelEvent = self.__on_table_scroll
        tableWidget.keyReleaseEvent = self.__on_table_scroll

        QueryTableWraper.wrap(self, tableWidget, fieldsMap, hiddenFields)

    def _on_table_show(self):
        if self.__cursor.closed:
            return

        rowCount = self._tableWidget.rowCount()

        try:
            data = Query.fetch_cursor(self.__cursor, self.__offset, self.__count)
        except Exception, err:
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self._tableWidget.tr('ERROR'), unicode(err), QtGui.QMessageBox.Ok, self._tableWidget).exec_()
            return

        self.__offset += len(data)
        if len(data) != self.__count:
            Query.close_cursor(self.__cursor)

        self.__tableWidget.setRowCount( rowCount + len(data) )

        for i, item in enumerate(data):
            for j, row_name in enumerate(self.__fields_map):
                self._tableWidget.setItem(rowCount+i, j, QTableWidgetItem(str(item[row_name])))

            for key in self._hidden_fields:
                self._tableWidget.setItem(rowCount+i, self._fields[key], QTableWidgetItem(str(item[key])))


    def __on_table_scroll(self, event=None):
        if type(event) == QtGui.QKeyEvent and (event.key() not in [QtCore.Qt.Key_Down, QtCore.Qt.Key_PageDown]):
            return QTableWidget.keyReleaseEvent(self._tableWidget, event)

        if self.__tableWidget.verticalScrollBar().value() != self._tableWidget.verticalScrollBar().maximum():
            if type(event) == QtGui.QWheelEvent:
                return QTableWidget.wheelEvent(self._tableWidget, event)
            else:
                return

        self._on_table_show()
