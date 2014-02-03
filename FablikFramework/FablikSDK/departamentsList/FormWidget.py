
from Form import Ui_departamentsList as Ui_Form
from formWraper import FormWraper
from PyQt4 import Qt,QtCore,QtGui
from formManager import FormManager
from fablikLibrary import Query

class departamentsList (FormWraper):
    def onInit(self, **kparams):
        self.setupForm(Ui_Form)

        QtCore.QObject.connect(self._widgets.insertButton, QtCore.SIGNAL("clicked ()"), self.onInsert)
        QtCore.QObject.connect(self._widgets.modifyButton, QtCore.SIGNAL("clicked ()"), self.onModify)
        QtCore.QObject.connect(self._widgets.deleteButton, QtCore.SIGNAL("clicked ()"), self.onDelete)

        self.departaments = {}

        data = Query.select('get_departaments')

        for item in data:
            treeItem = QtGui.QTreeWidgetItem()
            if not item.description:
                item.description = ''
            treeItem.setText(0, str(item.name))
            treeItem.setText(1, str(item.description))
            self.departaments[item.id] = treeItem

        top_levels = []
        for item in data:
            chItem = self.departaments[item.id]

            if not item.parent_id:
                top_levels.append(chItem)
                continue

            parItem = self.departaments.get(item.parent_id, None)

            if not parItem:
                raise Exception (self.tr('Departament parent ( %s ) is not found!'%item.parent_id))

            parItem.addChild(chItem)


        self._widgets.treeWidget.insertTopLevelItems(0, top_levels)
        for item in top_levels:
            self._widgets.treeWidget.expandItem(top_levels[0])


    def onInsert(self):
        print 'insert'
        FormManager.openForm('modifyDepartaments', parent=self, modality=True, is_create=True)

    def onModify(self):
        print 'modify'
        cur_dep = {'id': 1, 'name': 'test', 'description':'test descr'} #FIXME: get current departament

        FormManager.openForm('modifyDepartaments', parent=self, modality=True, is_create=False, departament=cur_dep )

    def onDelete(self):
        print 'delete'

        dep_name = 'test' #FIXME: get current departament
        ret = QtGui.QMessageBox(QtGui.QMessageBox.Question, self.tr('Question'), self.tr('You are realy want delete %s departament?'%dep_name), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, self).exec_()

        if ret == QtGui.QMessageBox.Yes:
            #TODO: call remote delete methof
            print 'deleting..'
        else:
            print 'no deleting...'
