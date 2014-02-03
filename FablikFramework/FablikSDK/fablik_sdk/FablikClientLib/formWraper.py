from PyQt4.QtGui import QMdiSubWindow, QEdit, QComboBox, QCheckBox, QRadioBox

'''
calling form example:
...
form = Form(parent, flags)   # Form is inherited of FormWraper
form.showForm(False, user_id=233)
'''

class FormWraper(QMdiSubWindow):
    def __init__(self, parent, flags):
        QMdiSubWindow.__init__(self, parent, flags)

        self.__isReadOnly = False
        self.__alwaysEnabled = []
        self.__disabledForReadOnly = []
        self.__widgets = None

    def onInit(self, **kparams):
        '''
        Implement this method in inherited class
        '''
        pass

    def isReadOnly(self):
        '''
        Use this method for read read only state of form
        '''
        return __isReadOnly

    def setupForm(self, FormClass):
        '''
        Use this method in inherited classes in onInit method for setuping widgets form
        '''
        self.__widgets = FormClass()
        self.__widgets.setupUi(self)

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

    def showForm(self, isReadOnly,  **kparams):
        self.__isReadOnly = isReadOnly

        self.onInit(self, kparams)

        if self.__widgets is None:
            raise Exception ('Form widgets is not assigned by onInit routine!')

        if self.__isReadOnly:
            self.__disableWidgets()

        self.show()

    def __disableWidgets(self):
        def checkClass(currClass):
            for cl in classList:
                if issubclass(currClass, cl):
                    return True
            return False

        classList = [QEdit, QComboBox, QCheckBox, QRadioBox]

        for item in dir(self.__widgets):
            if item.startswith('_'):
                continue

            obj = getattr(self.__widgets, item)
            if obj in self.__alwaysEnabled:
                continue

            if obj in self.__disabledForReadOnly:
                obj.setEnabled(True)
                continue

            if hasattr(obj,'__class__') and checkClass(obj.__class__):
                obj.setEnabled(True)

