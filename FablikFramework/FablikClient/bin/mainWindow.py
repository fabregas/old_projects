from PyQt4 import Qt,QtCore,QtGui
from forms import mainForm, configForm, authForm
from mainMenu import MainMenu
from configManager import Config
from soapClient import Client
from formManager import FormManager
from errorMessages import MESSAGES
from languageConfig import LangConfig
from logManager import LogManager
from fablikLibrary import Query
import sys, logging


class TranslateHolder:
    TRANS_LIST = []

    @classmethod
    def add_translator(cls, trans):
        cls.TRANS_LIST.append(trans)


def loadTranslateFile(lang_file, lang_path):
    translator = QtCore.QTranslator()

    TranslateHolder.add_translator(translator)

    if translator.load(lang_file, lang_path):
        QtGui.QApplication.installTranslator(translator)
    else:
        LogManager.error('translate file %s from is not loaded from %s' %(lang_file, lang_path))


class MainWindow(Qt.QMainWindow):
    def __init__(self):
        Qt.QMainWindow.__init__(self)

        self.form = mainForm.Ui_MainWindow()
        self.form.setupUi(self)

        Config.init_config()
        self.langConfig = LangConfig(Config.getLangConfig())
        if not Config.is_exists():
            self.showConfigWindow(isFirst=True)
        else:
            Config.read_config()
            self.showAuthForm()


    def closeEvent(self, event):
        asq = QtGui.QMessageBox(QtGui.QMessageBox.Question, self.tr('Exit'), self.tr('You are realy want exit now?'), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, self)

        ret = asq.exec_()

        if ret == QtGui.QMessageBox.Yes:
            try:
                FormManager.closeAllWindows()
                Client.close_session()
            except Exception, err:
                LogManager.warning('Closing session error. Details: %s' %(err))
            event.accept()
        else:
            event.ignore()


    def loadLanguage(self):
        lang_sid = Config.getLangSid()
        try:
            lang_name, lang_file = self.langConfig.getLanguage(lang_sid)
        except Exception, err:
            LogManager.error('Getting lang file error. Details: %s' %(err))
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self.tr('Error'), unicode(err), QtGui.QMessageBox.Ok, self).exec_()
            return

        translator = QtCore.QTranslator()

        TranslateHolder.add_translator(translator)

        if translator.load(lang_file, Config.getLangPath()):
            QtGui.QApplication.installTranslator(translator)
        else:
            LogManager.warning('Translation file %s is not loaded from %s' %(lang_file, Config.getLangPath()))
            QtGui.QMessageBox(QtGui.QMessageBox.Warning, self.tr('Warning'), self.tr('Translation file is not found'), QtGui.QMessageBox.Ok, self).exec_()

        MESSAGES.init()

    def showErrorMessage(self, title, message):
        LogManager.error('%s: %s' %(title, message))
        msg = QtGui.QMessageBox(QtGui.QMessageBox.Critical, title, message, QtGui.QMessageBox.Ok, self)
        msg.exec_()


    def loadMain(self):
        LogManager.info('Initiating main window... ')

        try:
            self.form.mdiArea.showErrorMessage = self.showErrorMessage

            FormManager.initFormCache(self.form.mdiArea, Config.getFormCacheDir(), Config.getFormRuntimeDir())
            sys.path.insert(1, Config.getFormRuntimeDir())

            self.menu = MainMenu(self.form)
            self.menu.create_menu(self)
            self.appendTechMenu()

            Query.init_query(Client.get_interface('FABLIK_QUERY'))

            self.showMaximized()
        ####w.showFullScreen()
        except Exception, err:
            LogManager.error('Loading main window error. Details: %s'%err)
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self.tr('Critical error'), str(err), QtGui.QMessageBox.Yes , None).exec_()

    def showAuthForm(self):
        def authenticate():
            login = form.loginEdit.text()
            password = form.passwordEdit.text()
            if len(login) == 0 or len(password) == 0:
                return

            try:
                Client.authenticate(login, password)
            except Exception, err:
                msg = QtGui.QMessageBox(QtGui.QMessageBox.Critical, self.tr('Authentication error'), self.tr('Error details: ')+unicode(err), QtGui.QMessageBox.Ok, dialog)
                msg.exec_()
            else:
                dialog.accept()
        def close_auth():
            if not  self.close():
                self.showAuthForm()

        self.loadLanguage()

        dialog = Qt.QDialog(self)
        form = authForm.Ui_Form()
        form.setupUi(dialog)
        form.loginEdit.setText(Config.USER_NAME)
        if Config.USER_NAME:
            form.passwordEdit.setFocus()

        QtCore.QObject.connect(form.pushButton, QtCore.SIGNAL("clicked()"), authenticate)
        QtCore.QObject.connect(dialog, QtCore.SIGNAL("rejected()"), close_auth)
        QtCore.QObject.connect(dialog, QtCore.SIGNAL("accepted()"), self.loadMain)

        dialog.show()

    def showConfigWindow(self, isFirst=False):
        logLevelMap = {0:logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4:logging.DEBUG}
        def save_config():
            text = form.lineEdit.text()
            if len(text) == 0:
                return

            if form.cascadeBtn.isChecked():
                ordering = 'cascade'
            else:
                ordering = 'tile'

            lang_sid = langMap[form.comboBox.currentIndex()][0]

            log_level = logLevelMap[form.logLevels.currentIndex()]

            Config.setServiceUrl(text)
            Config.setWindowsOrdering(ordering)
            Config.setLangSid(lang_sid)
            Config.setLogLevel(log_level)
            is_change_config = Config.save_config()
            Config.read_config()

            if not isFirst and is_change_config:
                QtGui.QMessageBox(QtGui.QMessageBox.Warning, self.tr('Warning'), self.tr('Some comfiguration patameters need restart application'), QtGui.QMessageBox.Ok, self).exec_()

            dialog.accept()

        def close_conf():
            if not  self.close():
                self.showConfigWindow(isFirst)

        dialog = Qt.QDialog(self)
        dialog.setModal(True)
        form = configForm.Ui_Form()
        form.setupUi(dialog)

        try:
            langMap = self.langConfig.getLanguages()
        except Exception, err:
            LogManager.error('Getting languages error. Details: %s' %(err))
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, self.tr('Error'), unicode(err), QtGui.QMessageBox.Ok, self).exec_()

        cur_idx = 0
        for item_id in langMap:
            form.comboBox.insertItem(item_id,langMap[item_id][1])
            if langMap[item_id][1] == Config.getLangSid():
                cur_idx = item_id

        form.comboBox.setCurrentIndex(cur_idx)

        log_level = Config.getLogLevel()
        for idx in logLevelMap:
            if logLevelMap[idx] == log_level:
                break
        form.logLevels.setCurrentIndex(idx)

        form.lineEdit.setText(Config.getServiceUrl())
        if Config.getWindowsOrdering() == 'cascade':
            form.cascadeBtn.setChecked(True)
        else:
            form.tileBtn.setChecked(True)

        QtCore.QObject.connect(form.pushButton, QtCore.SIGNAL("clicked()"), save_config)
        if isFirst:
            QtCore.QObject.connect(dialog, QtCore.SIGNAL("rejected()"), close_conf)
            QtCore.QObject.connect(dialog, QtCore.SIGNAL("accepted()"), self.showAuthForm)

        return dialog.show()

    def appendTechMenu(self):
        def create_item(menu, name, label, is_bold=False):
            action = QtGui.QAction(self)
            action.setObjectName(name)
            action.setText(label)
            font = action.font()
            font.setBold(is_bold)
            menu.addAction(action)
            #action.setStatusTip(menu.help_description)

        menubar = self.menuBar()

        menuWindow = QtGui.QMenu(menubar)
        menuWindow.setObjectName('TWindows')
        menuWindow.setTitle(self.tr('Windows'))
        menubar.addAction(menuWindow.menuAction())

        QtCore.QObject.connect(menuWindow, QtCore.SIGNAL("triggered (QAction *)"), self.onWindMenuClick)

        create_item(menuWindow, 'Cascade',  self.tr('Cascade windows'))
        create_item(menuWindow, 'Tile',     self.tr('Tile windows'))
        create_item(menuWindow, 'CloseAll', self.tr('Close all windows'))

        menuWindow.addSeparator()

        cur_id = FormManager.getCurrentFormID()
        ids = FormManager.getActiveFormsID()
        for fid in ids:
            label = ids[fid]
            if len(label) > 50:
                label = label[:47] + '...'

            if fid == cur_id:
                is_bold = True
            else:
                is_bold = False

            create_item(menuWindow, 'form%i'%fid,label, is_bold)

        menuWindow.addSeparator()
        create_item(menuWindow, 'Settings', self.tr('Settings...'))



    def onWindMenuClick(self, action):
        objName = str(action.objectName())

        if objName == 'Cascade':
            FormManager.cascadeWindows()
        elif objName == 'Tile':
            FormManager.tileWindows()
        elif objName == 'CloseAll':
            FormManager.closeAllWindows()
        elif objName == 'Settings':
            self.showConfigWindow()
        elif objName.startswith('form'):
            FormManager.activateForm(int(objName[4:]))
