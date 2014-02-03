from PyQt4.QtGui import QLineEdit, QComboBox, QCheckBox, QRadioButton, QDialog, QPushButton,QTextEdit
from PyQt4 import QtCore,QtGui

'''
calling form example:
...
form = Form(parent, flags)   # Form is inherited of FormWraper
form.showForm(False, user_id=233)
'''

class FormWraper(QDialog):
    permissions = 0
    active_contexts = {}
    send_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.__isReadOnly = False
        self.__alwaysEnabled = []
        self.__disabledForReadOnly = []
        self._widgets = None
        self.context = ''
        self.form_sid = ''

    def closeEvent(self, event):
        del_c = None
        for i, (context, wind) in enumerate(self.active_contexts.get(self.form_sid,[])):
            if context == self.context:
                del_c = i
                break
        if del_c:
            del self.active_contexts[self.form_sid][del_c]

        if self.onClose():
            event.ignore()
        else:
            event.accept()


    def onInit(self, **kparams):
        '''
        Implement this method in inherited class
        '''
        pass

    def onClose(self):
        '''
        Implement this method in inherited class for freeing resources
        return True value for disabling closing this form
        '''
        pass

    def setReadOnly(self):
        self.__isReadOnly = True

    def isReadOnly(self):
        '''
        Use this method for read read only state of form
        '''
        return self.__isReadOnly

    def setupForm(self, FormClass):
        '''
        Use this method in inherited classes in onInit method for setuping widgets form
        '''
        self._widgets = FormClass()
        self._widgets.setupUi(self)

    def setAlwaysEnabled(self, widget):
        '''
        Use this method in inherited classes for enabling widget state for ReadOnly form
        '''
        self.__alwaysEnabled.append(widget)

    def setDisableForReadOnly(self, widget):
        '''
        Use this method in inherited classes for disabling widget state for ReadOnly form
        '''
        self.__disabledForReadOnly.append(widget)

    def createForm(self, form_sid, **kparams):
        self.form_sid = form_sid
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.onInit(**kparams)

        if self._widgets is None:
            raise Exception ('Form widgets is not assigned by onInit routine!')

        if self.__isReadOnly:
            self.__disableWidgets()

        self.setMinimumSize(self.width(),self.height())


    def __disableWidgets(self):
        def checkClass(currClass):
            for cl in classList:
                if issubclass(currClass, cl):
                    return True
            return False

        classList = [QLineEdit, QComboBox, QCheckBox, QRadioButton, QPushButton, QTextEdit]

        for item in dir(self._widgets):
            if item.startswith('_'):
                continue

            obj = getattr(self._widgets, item)

            if obj in self.__alwaysEnabled:
                continue

            if obj in self.__disabledForReadOnly and hasattr(obj, 'setEnabled'):
                obj.setEnabled(False)
                continue

            if hasattr(obj,'__class__') and checkClass(obj.__class__):
                obj.setEnabled(False)

    def getFormSID(self):
        return self.form_sid

    def sendToParentForm(self, data):
        self.send_data_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def onChildData(self,data):
        pass

    def errorMessage(self, message):
        QtGui.QMessageBox(QtGui.QMessageBox.Critical, self.tr('ERROR'), unicode(message), QtGui.QMessageBox.Ok, self).exec_()

    def warningMessage(self, message):
        QtGui.QMessageBox(QtGui.QMessageBox.Warning, self.tr('WARNING'), unicode(message), QtGui.QMessageBox.Ok, self).exec_()

    def informationMessage(self, message):
        QtGui.QMessageBox(QtGui.QMessageBox.Information, self.tr('INFORMATION'), unicode(message), QtGui.QMessageBox.Ok, self).exec_()

    def askQuestion(self, question):
        asq = QtGui.QMessageBox(QtGui.QMessageBox.Question, self.tr('Question'), unicode(question), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, self)
        ret = asq.exec_()

        if ret == QtGui.QMessageBox.Yes:
            return True
        return False
