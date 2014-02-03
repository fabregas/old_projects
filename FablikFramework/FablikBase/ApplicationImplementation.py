from IOTypesStructure import *

import hashlib,thread

from FablikBaseLib import FablikBaseLib
from FablikBaseLib.FablikErrorCodes import *

from IOTypesStructure import binary

# MenuItem  and  URL incapsulate objects for caching...

class MenuItem:
    def __init__(self, item_raw):
        self.id = item_raw[0]
        self.parent_id = item_raw[1]
        if not item_raw[2]:
            self.form_sid = None
        else:
            self.form_sid = str(item_raw[2])
        self.name = item_raw[3]
        self.help_description = item_raw[4]
        self.shortcut = item_raw[5]

    def update_checksum(self, hashed):
        hashed.update(str(self.id))
        hashed.update(str(self.parent_id))
        hashed.update(str(self.form_sid))
        hashed.update(str(self.name))
        hashed.update(str(self.help_description))
        hashed.update(str(self.shortcut))

class URL:
    def __init__(self, item_raw):
        self.id = item_raw[0]
        self.sid = item_raw[1]
        self.service_url = item_raw[2]
        self.description = item_raw[3]

    def update_checksum(self, hashed):
        hashed.update(str(self.id))
        hashed.update(str(self.sid))
        hashed.update(str(self.service_url))
        hashed.update(str(self.description))


def my_cmp(a, b):
    # function for compare URL and MenuItem ibjects by ID (for valid hashing...)

    if a.id > b.id:
        return 1
    return -1



class FablikBaseImplementation:
    def start_routine(self, config):
        self.base_lib = FablikBaseLib.FablikBaseRoutines(config)
        self.__lock = thread.allocate_lock()

        self.synchronize(config)


    def synchronize(self, config):
        self.base_lib.synchronize(config)
        self.debug = config.get('DEBUG',False)

        #make cache
        urls_cache = []

        urls = self.base_lib.getInterfaces()
        for item in urls:
            urls_cache.append(URL(item))

        self.__lock.acquire_lock()

        self.urls_cache = urls_cache

        self.__lock.release_lock()


    def get_urls_cache(self):
        self.__lock.acquire_lock()
        ret = self.urls_cache
        self.__lock.release_lock()

        return ret


    def stop_routine(self):
        del self.base_lib

    def authenticate(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        session_id = ''

        try:

            user_id, session_id = self.base_lib.authenticate(request.login, request.password)

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseAuthenticate(ret_code=err_code, ret_message=err_message, session_id=session_id)

    def authorize(self, request):
        err_code, err_message, is_auth = (FBE_OK, 'ok', 0)
        try:
            is_auth = self.base_lib.authorize(request.session_id, request.role_sid)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseAuthorize(ret_code=err_code, ret_message=err_message, is_authorize=int(is_auth))

    def closeSession(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        try:
            self.base_lib.closeSession(request.session_id)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseCloseSession(ret_code=err_code, ret_message=err_message)

    def getMainMenu(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        menu_list = []

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            user_menu = []
            menu = self.base_lib.getUserMenus(request.lang_sid, user_id)
            for item in menu:
                user_menu.append(MenuItem(item))

            user_menu.sort(cmp=my_cmp)
            md5 = hashlib.md5()
            for item in user_menu:
                item.update_checksum(md5)

            menu_checksum = md5.hexdigest()

            if menu_checksum != request.checksum:
                for item in user_menu:
                    menu_list.append(MenuItemType(id=item.id, parent_id=item.parent_id, form_sid=item.form_sid, name=item.name, help=item.help_description,shortcut=item.shortcut))
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseGetMainMenu(ret_code=err_code, ret_message=err_message, menu_list=menu_list)


    def getInterfaces(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        urls_list = []

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            urls = self.get_urls_cache()

            for item in urls:
                urls_list.append(InterfaceType(sid=item.sid, url=item.service_url))
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseGetInterfaces(ret_code=err_code, ret_message=err_message,  interface_list=urls_list)


    def getForm(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        perm, form, form_id = 0, '', None

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            (form_id,form,perm) = self.base_lib.getForm(request.form_sid, user_id, request.checksum)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseGetForm(ret_code=err_code, ret_message=err_message, form_id=form_id, form_source = binary.Attachment(encoded_data=form), form_permission = perm)

