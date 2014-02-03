
from Form import Ui_departments
from formWraper import FormWraper
from logManager import LogManager
from fablikLibrary import TreeWraper, Query, rw_form_only
from soapClient import Client
from configManager import Config
from PyQt4 import QtGui

class departments (FormWraper):
    def onInit(self, **kparams):
        self.setupForm(Ui_departments)

        self.mgt_interface = Client.get_interface('FABLIK_MGT')

        self.syncTree()

        self._widgets.departmentsTree.setColumnWidth(0, 250)
        self._widgets.departmentsTree.setColumnWidth(1, 150)

        self.disable_edits()

        self._widgets.allRolesList.clear()
        self.all_roles = Query.select('GET_ROLES')
        for role in self.all_roles:
            self._widgets.allRolesList.addItem(role['sid'])

        #connect signals
        self._widgets.newDepBtn.clicked.connect(self.onCreateNewDepartment)
        self._widgets.newSubDepBtn.clicked.connect(self.onCreateSubDepartment)
        self._widgets.remDepBtn.clicked.connect(self.onRemoveDepartment)
        self._widgets.applyBtn.clicked.connect(self.onApplyDepartment)

        self._widgets.departmentsTree.itemSelectionChanged.connect(self.fill_edits)

    def syncTree(self):
        self._widgets.departmentsTree.clear()
        self.treeWraper = TreeWraper('GET_DEPARTMENTS')
        self.treeWraper.wrap(self._widgets.departmentsTree, 'id', 'parent_id', ['name','sid','description'], ['id','parent_id'])

        self._widgets.departmentsTree.expandAll()

    def disable_edits(self):
        wl = self._widgets
        wl.depNameEdit.setDisabled(True)
        wl.depSIDEdit.setDisabled(True)
        wl.depDescriptionEdit.setDisabled(True)

    @rw_form_only
    def enable_edits(self):
        wl = self._widgets
        wl.depNameEdit.setDisabled(False)
        wl.depSIDEdit.setDisabled(False)
        wl.depDescriptionEdit.setDisabled(False)

    def fill_edits(self, dummy1='', dummy2=''):
        self.enable_edits()
        wl = self._widgets

        line = self.treeWraper.getCurrentItemLine()
        wl.depNameEdit.setText(line['name'])
        wl.depSIDEdit.setText(line['sid'])
        wl.depDescriptionEdit.setText(line['description'])
        wl.disabledRolesList.clear()

        if line['id'] == '':
            return

        try:
            dep_roles = Query.select('GET_DEP_DISABLED_ROLES', department_id=line['id'])
        except Exception, err:
            self.errorMessage(err)

        for role in dep_roles:
            wl.disabledRolesList.addItem(role['sid'])


    def onCreateNewDepartment(self):
        wl = self._widgets
        new_item = QtGui.QTreeWidgetItem(wl.departmentsTree, [self.tr('New root item...')])

        wl.departmentsTree.setCurrentItem(new_item)
        wl.depNameEdit.selectAll()
        wl.depNameEdit.setFocus()

    def onCreateSubDepartment(self):
        wl = self._widgets
        cur_item = wl.departmentsTree.currentItem()
        dep_id = self.treeWraper.getCurrentItem('id')
        if dep_id == '':
            self.warningMessage(self.tr('Edited department is not saved! Subdepartment creating is not possible.'))
            return

        new_item = QtGui.QTreeWidgetItem(cur_item, [self.tr('New subitem...'),'','','',dep_id])
        wl.departmentsTree.setCurrentItem(new_item)
        wl.depNameEdit.selectAll()
        wl.depNameEdit.setFocus()


    def onApplyDepartment(self):
        wl = self._widgets

        dep_id = self.treeWraper.getCurrentItem('id')
        dep_name = wl.depNameEdit.text()
        dep_sid = wl.depSIDEdit.text()
        dep_descr = wl.depDescriptionEdit.text()

        if dep_name == '':
            self.errorMessage(self.tr('Departmnent name must be not empty!'))
            return

        if dep_sid == '':
            self.errorMessage(self.tr('Department SID must be not empty'))
            return

        if dep_id:
            in_var = self.mgt_interface.create_variable('RequestUpdateDepartment')
            in_var.department_id = dep_id
        else:
            in_var = self.mgt_interface.create_variable('RequestCreateDepartment')

        in_var.session_id = Config.getSessionID()
        in_var.sid = dep_sid
        in_var.parent_id = self.treeWraper.getCurrentItem('parent_id')
        in_var.name = dep_name
        in_var.description = dep_descr

        if dep_id:
            method = 'updateDepartment'
        else:
            method = 'createDepartment'

        ret = self.mgt_interface.call(method, in_var)

        if ret.ret_code != 0:
            self.errorMessage(ret.ret_message)
            return

        self.informationMessage(self.tr('Department is saved in database'))

        self.syncTree()

    def onRemoveDepartment(self):
        dep_id = self.treeWraper.getCurrentItem('id')
        if not dep_id:
            curr = self._widgets.departmentsTree.currentItem()
            if not curr:
                return
            p = curr.parent()
            p.removeChild(curr)
            return

        yes = self.askQuestion(self.tr('Do you realy want delete this department?'))
        if not yes:
            return

        in_var = self.mgt_interface.create_variable('RequestDeleteDepartment')

        in_var.session_id = Config.getSessionID()
        in_var.department_id = dep_id

        ret = self.mgt_interface.call('deleteDepartment', in_var)

        if ret.ret_code != 0:
            self.errorMessage(ret.ret_message)
            return

        self.informationMessage(self.tr('Department is deleted from database'))

        self.syncTree()
