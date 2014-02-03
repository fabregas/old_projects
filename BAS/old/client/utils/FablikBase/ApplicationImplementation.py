from IOTypesStructure import *

import traceback,sys,hashlib,thread

from FablikSharedLib import FablikSharedLib


# MenuItem  and  URL incapsulate objects for caching...

class MenuItem:
    def __init__(self, item_raw):
        self.id = item_raw[0]
        self.parent_id = item_raw[1]
        self.role_id = item_raw[2]
        self.form_id = item_raw[3]
        self.name = item_raw[4]
        self.help_description = item_raw[5]
        self.shortcut = item_raw[6]
    

    def update_checksum(self, hashed):
        hashed.update(str(self.id))
        hashed.update(str(self.parent_id))
        hashed.update(str(self.form_id))
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
        self.base_lib = FablikSharedLib.FablikBaseLibrary(config)
        self.__lock = thread.allocate_lock()

        self.syncronize_application(config)


    def syncronize_application(self, config):
        self.base_lib.syncronize(config)
        self.debug = config.get('DEBUG',0)

        #make cache
        menu_cache = []
        urls_cache = []

        menu = self.base_lib.getMenus()
        for item in menu:
            menu_cache.append(MenuItem(item))


        urls = self.base_lib.getInterfaces()
        for item in urls:
            urls_cache.append(URL(item))

        urls_cache.sort(cmp=my_cmp)
        md5 = hashlib.md5()
        for item in urls_cache:
            item.update_checksum(md5)

        self.urls_checksum = md5.hexdigest()

        self.__lock.acquire_lock()

        self.menu_cache = menu_cache
        self.urls_cache = urls_cache

        self.__lock.release_lock()

    def get_menu_cache(self):
        self.__lock.acquire_lock()
        ret = self.menu_cache
        self.__lock.release_lock()

        return ret

    def get_urls_cache(self):
        self.__lock.acquire_lock()
        ret = self.urls_cache,self.urls_checksum
        self.__lock.release_lock()

        return ret


    def stop_routine(self):
        del self.base_lib


    def parse_exception(self,e_obj):
        if len(e_obj.args) == 2:
            (err_code, err_message) = e_obj.args
        else:
            (err_code,err_message) = (-1, str(e_obj))

        if self.debug:
            err_message += '\n' + '-'*80 + '\n'
            err_message += ''.join(apply(traceback.format_exception, sys.exc_info()))
            err_message += '-'*80 + '\n'

        return (err_code, err_message)

    def authenticate(self, request):
        err_code, err_message = (0, 'ok')
        session_id = ''
        roles_list = []

        try:
            user_id, session_id = self.base_lib.authenticate(request.login, request.password)

            roles = self.base_lib.getUserRoles(user_id)

            for item in roles:
                roles_list.append(role(sid=item[1]))
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseAuthenticate(ret_code=err_code, ret_message=err_message, session_id=session_id, roles_list=roles_list)


    def getMainMenu(self, request):
        err_code, err_message = (0, 'ok')
        menu_list = []

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)
            user_roles = self.base_lib.getUserRoles(user_id)
            user_roles = [i[0] for i in user_roles]

            menu = self.get_menu_cache()

            user_menu = []
            for item in menu:
                if item.role_id in user_roles:
                    user_menu.append(item)

            user_menu.sort(cmp=my_cmp)
            md5 = hashlib.md5()
            for item in user_menu:
                item.update_checksum(md5)

            menu_checksum = md5.hexdigest()

            if menu_checksum != request.checksum:
                for item in user_menu:
                    menu_list.append(menu_item(id=item.id, parent_id=item.parent_id, form_id=item.form_id, name=item.name, help=item.help_description,shortcut=item.shortcut))
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseGetMainMenu(ret_code=err_code, ret_message=err_message, menu_list=menu_list)


    def getInterfaces(self, request):
        err_code, err_message = (0, 'ok')
        urls_list = []
            
        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            urls, checksum = self.get_urls_cache()

            if checksum != request.checksum:
                for item in urls:
                    urls_list.append(interface(sid=item.sid, service_url=item.service_url))
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseGetInterfaces(ret_code=err_code, ret_message=err_message,  interface_list=urls_list)

    def getDepartaments(self, request):
        departaments_list = []
        err_code = 0
        err_message = 'ok'

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            departaments = self.base_lib.getDepartaments(request.root_departament_id)

            for item in departaments:
                departaments_list.append(departament(id=item[0], parent_id=item[1], name=item[2]))
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)


        return ResponseGetDepartaments(ret_code=err_code, ret_message=err_message, departament_list=departaments_list)

    def getPositions(self, request):
        positions_list = []
        err_code = 0
        err_message = 'ok'

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            positions = self.base_lib.getPositions(request.root_position_id)

            for item in positions:
                positions_list.append(position(id=item[0], parent_id=item[1], name=item[2]))
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)


        return ResponseGetPositions(ret_code=err_code, ret_message=err_message,position_list= positions_list)


    def appendPosition(self, request):
        err_code, err_message, position_id = (0,'ok',None)

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            position_id = self.base_lib.appendPosition(request.parent_position_id, request.name, request.description)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseAppendPosition(ret_code=err_code, ret_message=err_message, position_id=position_id)

    def updatePosition(self, request):
        err_code, err_message = (0,'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            self.base_lib.updatePosition(request.position_id, request.parent_position_id, request.name, request.description)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseUpdatePosition(ret_code=err_code, ret_message=err_message)

    def deletePosition(self, request):
        err_code, err_message = (0,'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            self.base_lib.deletePosition(request.position_id)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseDeletePosition(ret_code=err_code, ret_message=err_message)

    def appendDepartament(self, request):
        err_code, err_message,departament_id = (0,'ok',None)

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            departament_id = self.base_lib.appendDepartament(request.parent_departament_id, request.name, request.description)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseAppendDepartament(ret_code=err_code, ret_message=err_message, departament_id=departament_id)

    def updateDepartament(self, request):
        err_code, err_message = (0,'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            self.base_lib.updateDepartament(request.departament_id, request.parent_departament_id, request.name, request.description)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseUpdateDepartament(ret_code=err_code, ret_message=err_message)

    def deleteDepartament(self, request):
        err_code, err_message = (0,'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            self.base_lib.deleteDepartament(request.departament_id)
        except Exception, e_obj:
            err_code, err_message = self.parse_exception(e_obj)

        return ResponseDeleteDepartament(ret_code=err_code, ret_message=err_message)

