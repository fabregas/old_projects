
from Form import Ui_modifyDepartaments as Ui_Form
from formWraper import FormWraper

class modifyDepartaments (FormWraper):
    def onInit(self, **kparams):
        self.setupForm(Ui_Form)

        #write init code at this point...
        isCreate =  kparams.get('is_create',False)

        if isCreate:
            self.sendToParentForm({'test':344})
        else:
            self.sendToParentForm({'test':'modifying...'})


    def closeEvent(self, event):
        print 'event:', event
