from soapClient import Client
from configManager import Config
import os,base64,zipfile,shutil,hashlib
import mainWindow

PERM_READ   = 1
PERM_WRITE  = 2

class FormManager:
    @classmethod
    def initFormCache(cls, mdi_parent, cache_directory='.', runtime_directory='.'):
        cls.__form_cache = {} # cached forms. Key - form_sid, Value - form_class

        cls.__cache_dir = cache_directory
        cls.__run_dir = runtime_directory

        #load __forms_sids dict from local directory
        cls.__init_cache()

        cls.__mdi_parent = mdi_parent

    @classmethod
    def __init_cache(cls):
        try:
            if not os.path.exists(cls.__cache_dir):
                os.mkdir(cls.__cache_dir)
            if not os.path.exists(cls.__run_dir):
                os.mkdir(cls.__run_dir)

            d_entry = os.listdir(cls.__cache_dir)

            for element in d_entry:
                if element.endswith('.ffc'):
                    form_sid = element[:-4]
                    cls.__form_cache[form_sid] = None
        except Exception, err:
            print 'Error: init cache failed. Details: %s'%err


    @classmethod
    def __load_form_by_sid(cls, form_sid, checksum=''):
        iface = Client.get_interface('FABLIK_BASE')
        inputVar = iface.create_variable('RequestGetForm')

        inputVar.session_id = Config.getSessionID()
        inputVar.form_sid = form_sid
        inputVar.checksum = checksum

        result = iface.call('getForm', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        if result.form_source:
            print 'cache is not found or not valid. Creating...'
            form_source = base64.decodestring(result.form_source)
            f = open(os.path.join(cls.__cache_dir, '%s.ffc'%(form_sid)), 'wb')
            f.write(form_source)
            f.close()

        return result.form_permission

    @classmethod
    def __load_form_lang(cls, form_path):
        lang_sid = Config.getLangSid()

        lang_file = 'translate_%s.qm' % lang_sid

        mainWindow.loadTranslateFile(lang_file, os.path.join(form_path,'lang'))


    @classmethod
    def __load_from_local(cls, form_sid):
        #check form checksum
        cfile = os.path.join(cls.__cache_dir, '%s.ffc'%(form_sid))
        if os.path.exists(cfile):
            md5 = hashlib.md5()
            md5.update(open(cfile,'rb').read())
            checksum = md5.hexdigest()
        else:
            checksum = ''

        form_perm = cls.__load_form_by_sid(form_sid, checksum)


        #unzip local file
        source_file = zipfile.ZipFile(cfile)
        form_path = os.path.join(cls.__run_dir, form_sid)

        try:
            shutil.rmtree(form_path)
        except: pass

        os.mkdir(form_path)
        source_file.extractall(form_path)

        #import form
        exec("import %s.FormWidget as FormModule"%(form_sid))
        exec("form_class = FormModule.%s"%(form_sid))

        #append form to cached forms
        cls.__form_cache[form_sid] = form_class
        form_class.active_contexts[form_sid] = []

        #load lang...
        cls.__load_form_lang(form_path)

        return form_perm

    @classmethod
    def __show_form(cls, form_sid, form, parent, modality, **kparams):
        if form.permissions not in [PERM_READ, PERM_WRITE]:
            raise Exception ('You are not permissions for open this form')

        formInst = form(parent)

        if form.permissions is PERM_READ:
            formInst.setReadOnly()

        #if modality:    #FIXME fix MdiSubwindow modality...
        #    formInst.setModal(modality)

        formInst.createForm(form_sid, **kparams)

        if parent:
            formInst.send_data_signal.connect(parent.onChildData)
            formInst.context = parent.objectName()
            formInst.setWindowTitle("[%s] %s"% (parent.windowTitle(),formInst.windowTitle()))
        else:
            formInst.context = 'topWidget'


        child = cls.__mdi_parent.addSubWindow(formInst)
        formInst.active_contexts[form_sid].append((formInst.context, child))

        child.showNormal()


    @classmethod
    def checkContext(cls, parent, wind, form_sid):
        if not parent:
            context = 'topWidget'
        else:
            context = parent.objectName()

        for (ctxt, subwind) in wind.widget().active_contexts[form_sid]:
            if ctxt == context:
                return subwind

        return None


    @classmethod
    def openForm(cls, form_sid, parent=None, modality=False, **kparams):
        form = cls.__form_cache.get(form_sid, None)

        try:
            if form is None: # form is not loaded
                form_perm = cls.__load_from_local(form_sid)
                form = cls.__form_cache[form_sid]
                form.permissions = form_perm
            else:
                #check in opened forms...
                windList = cls.__mdi_parent.subWindowList()
                for wind in windList:
                    subwind = cls.checkContext(parent, wind, form_sid)
                    if subwind:
                        cls.__mdi_parent.setActiveSubWindow(subwind)
                        return

            return cls.__show_form(form_sid, form, parent, modality, **kparams)
        except Exception, err:
            cls.__mdi_parent.showErrorMessage( 'Loading form error', 'Error details: '+str(err))


    @classmethod
    def closeForm(cls, form_id):
        pass

    @classmethod
    def activateForm(cls, form_id):
        print 'activating %i form'%form_id

    @classmethod
    def getCurrentFormID(cls):
        return 5

    @classmethod
    def getActiveFormsID(cls):
        return {5:'Test window 1', 654:'Test window 2 and long window name with strip method'}

    @classmethod
    def cascadeWindows(cls):
        cls.__mdi_parent.cascadeSubWindows()

    @classmethod
    def tileWindows(cls):
        cls.__mdi_parent.tileSubWindows()

    @classmethod
    def closeAllWindows(cls):
        cls.__mdi_parent.closeAllSubWindows()

