
from PyQt4 import QtCore,QtGui
import hashlib, pickle
from soapClient import Client
from configManager import Config
from formManager import FormManager
from logManager import LogManager


class MenuItem:
    def __init__(self, menu_id, help_description, menu_label, form_sid, form_md5, parent_id=None, shortcut=''):
        self.menu_id = menu_id
        self.menu_sid = "menu#%s" % self.menu_id
        self.menu_label = unicode( menu_label )
        self.help_description = unicode( help_description )
        self.shortcut = str( shortcut )
        self.form_sid = str (form_sid )
        self.form_md5 = str (form_md5)
        self.parent_id = parent_id

        self.menu = None


    def update_checksum(self, hashed):
        hashed.update(str(self.menu_id))
        hashed.update(str(self.parent_id))
        hashed.update(str(self.form_sid))
        hashed.update(self.menu_label.encode('utf8'))
        hashed.update(self.help_description.encode('utf8'))
        hashed.update(str(self.shortcut))

    def __getstate__(self):
        return (self.menu_id, self.menu_sid,self.menu_label, self.help_description, self.shortcut, self.form_sid, self.form_md5, self.parent_id)


    def __setstate__(self, state):
        self.menu_id = state[0]
        self.menu_sid = state[1]
        self.menu_label = state[2]
        self.help_description = state[3]
        self.shortcut = state[4]
        self.form_sid = state[5]
        self.form_md5 = state[6]
        self.parent_id = state[7]




def my_cmp(a, b):
    # function for compare MenuItem ibjects by ID (for valid hashing...)
    if a.menu_id > b.menu_id:
        return 1
    return -1


class MainMenu:
    def __init__(self, main_form):
        self.__menu_cache_file = Config.MENU_CACHE
        self.__menu = []
        self.__main_form = main_form

    def _save_cache(self):
        f = open(self.__menu_cache_file, 'wb')

        pickle.dump(self.__menu, f)

        f.close()

    def load_menu(self):
        f = None
        try:
            f = open(self.__menu_cache_file, 'rb')
            self.__menu = pickle.load(f)
        except Exception,e:
            LogManager.info('Menu cache %s is not loaded. Details: %s' %(self.__menu_cache_file,e))
        finally:
            if f is not None:
                f.close()

        self.__menu.sort(cmp=my_cmp)
        md5 = hashlib.md5()
        for item in self.__menu:
            item.update_checksum(md5)

        menu_checksum = md5.hexdigest()

        iface = Client.get_interface('FABLIK_BASE')
        inputVar = iface.create_variable('RequestGetMainMenu')

        inputVar.session_id = Config.getSessionID()
        inputVar.checksum = menu_checksum
        inputVar.lang_sid = Config.getLangSid()

        result = iface.call('getMainMenu', inputVar)

        if result.ret_code != 0:
            raise Exception(result.ret_message)

        if len(result.menu_list) == 0:
            LogManager.info('Menu cache is valid. Use it')
            return

        self.__menu = []
        for item in result.menu_list[0]:
            menuitem = MenuItem(item.id, item.help, item.name, item.form_sid, 0, item.parent_id, item.shortcut)

            self.__menu.append(menuitem)

        self._save_cache()
        LogManager.info('Menu loaded and saved to local cache file (%s)'%self.__menu_cache_file)


    def create_menu(self, MainWindow):
        if len(self.__menu) == 0:
            self.load_menu()

        menubar = self.__main_form.menubar

        for menu in self.__menu:
            if menu.parent_id == None:
                menuWindow = QtGui.QMenu(menubar)
                menuWindow.setObjectName(menu.menu_sid)
                menuWindow.setTitle(menu.menu_label)
                menu.menu = menuWindow
                menubar.addAction(menuWindow.menuAction())

                QtCore.QObject.connect(menuWindow, QtCore.SIGNAL("triggered (QAction *)"), self.menuClick)


        for menu in self.__menu:
            if menu.parent_id != None:
                action = QtGui.QAction(MainWindow)
                action.setObjectName(menu.menu_sid)
                action.setText(menu.menu_label)
                action.setStatusTip(menu.help_description)

                if menu.shortcut:
                    action.setShortcut( menu.shortcut )

                for p_menu in self.__menu:
                    if p_menu.menu_id == menu.parent_id:
                        p_menu.menu.addAction(action)
                        break
                menu.menu = action



    def menuClick(self,  action ):
        name = action.objectName()
        for menu in self.__menu:
            if menu.menu_sid == name:
                LogManager.info('Opening form with sid %s' %menu.form_sid)
                FormManager.openForm(menu.form_sid)
                LogManager.info('Form with sid %s is opened' %menu.form_sid)

                break
