import sql_fablik_lib as SQL
import thread
from SharedDBConnection import DBConnection
import hashlib,uuid
from FablikErrorCodes import *

PERM_READ = 1
PERM_WRITE = 2

class FablikBaseRoutines:
    def __init__(self, config_map):
        self.__lock = thread.allocate_lock()

        self.synchronize(config_map)


    def _get_audit_type(self, auditTypeSid, default):
        self.__lock.acquire_lock()
        val = self.audit_types.get(auditTypeSid, default)
        self.__lock.release_lock()

        return val

    def _get_object_type(self, auditObjectSid, default):
        self.__lock.acquire_lock()
        val = self.object_types.get(auditObjectSid, default)
        self.__lock.release_lock()

        return val


    def get_database_connection(self):
        return self.database

    def synchronize(self, config):
        DATABASE_STRING = config.get('FB_DATABASE_STRING',None)
        DATABASE_PSWD = config.get('FB_DATABASE_PASSWORD',None)

        if DATABASE_STRING is None or DATABASE_PSWD is None:
            raise Exception(FBE_CONFIG_ERROR,'FB_DATABASE_STRING and FB_DATABASE_PASSWORD must be set for this cluster')

        self.database = DBConnection.create_connection( DATABASE_STRING % DATABASE_PSWD )

        self.audit_level = config.get('AUDIT_LEVEL',5)

        audittypes= self.database.execute(SQL.get_audittype)

        audit_types = {}
        for atype in audittypes:
            audit_types[atype[1]] = (atype[0],atype[2])


        objectstypes= self.database.execute(SQL.get_objectstype)
        object_types = {}
        for atype in objectstypes:
            object_types[atype[1]] = atype[0]


        self.__lock.acquire_lock()
        self.audit_types = audit_types
        self.object_types = object_types
        self.__lock.release_lock()



    def authorize(self, session_id, role_sid):
        auth = self.database.execute(SQL.authorize % (session_id, role_sid))

        return auth[0][0]


    def authenticate(self, login, password):
        session_id = ''

        pwd = self.database.execute(SQL.get_password_hash % login)

        if not pwd:
            raise Exception(FBE_INVALID_USER, 'User %s is not found!'%login)

        md5 = hashlib.md5()
        md5.update(password)
        pwd_hash = md5.hexdigest()

        if pwd_hash != pwd[0][0]:
            raise Exception (FBE_INVALID_PASSWORD, 'Password is invalid')

        session_id = uuid.uuid4().hex

        user_id = pwd[0][1]
        session = self.database.execute(SQL.get_session % user_id)
        if session:
            self.closeSession(session[0][0])

        self.database.modify(SQL.insert_session % (session_id,user_id))

        return user_id, session_id

    def closeSession(self, session_id):
        self.database.modify(SQL.remove_cursors % session_id)
        self.database.modify(SQL.remove_session % session_id)

    def auth_by_session(self, session_id):
        session = self.database.execute(SQL.get_session_by_id % session_id)

        if not session:
            raise Exception(FBE_INVALID_SESSION, 'Session is not found!')

        return session[0][0]


    def addAudit(self, auditObject, auditObjectID, auditType, message):
        try:
            atype = self._get_audit_type(auditType, None)

            if atype is None:
                raise Exception(FBE_INVALID_AUDIT_TYPE, "Audit type '%s' is not found" % auditType)

            (type_id, audit_level) = atype

            if self.audit_level < audit_level:
                return

            obj_type_id = self._get_object_type(auditObject, None)

            if obj_type_id is None:
                raise Exception(FBE_INVALID_AUDIT_OBJECT ,"Audit object '%s' is not found" % auditObject)

            try:
                if auditObjectID is None:
                    auditObjectID = 0
                else:
                    auditObjectID = int(auditObjectID)
            except:
                raise Exception(FBE_INVALID_AUDIT_ID, "Audit object ID id must be integer")


            try:
                message = str(message)
            except:
                raise Exception(FBE_INVALID_AUDIT_MESSAGE, "Audit message must be string")

            self.database.modify(SQL.insert_audit % (obj_type_id, auditObjectID, type_id, message))
        except Exception, msg:
            raise Exception(str(msg))


    def getUserMenus(self, lang_sid, user_id):
        lang = self.database.execute(SQL.get_lang % lang_sid)
        if not lang:
            raise Exception (FBE_INVALID_LANG, 'Language with sid %s is not supported in system!' % lang_sid)

        lang_id = lang[0][0]

        menus = self.database.execute(SQL.get_menu % locals())

        return menus

    def getInterfaces(self):
        urls = self.database.execute(SQL.get_interfaces)

        return urls

    def __get_relative(self, dep_map, root_id, ret_list):
        el = dep_map.get(root_id,None)

        if el is None:
            raise Exception(FBE_INVALID_DEPARTAMENT, 'Root ID is not found')

        ret_list.append((root_id, el[0], el[1]))

        children = []
        for key in dep_map:
            if dep_map[key][0] == root_id:
                children.append(key)

        for item in children:
            self.__get_relative(dep_map, item, ret_list)


    def getDepartments(self, root_id):
        departments = self.database.execute(SQL.get_departments)

        if root_id:
            ret_list = []

            dep_map = {}
            for dep in departments:
                dep_map[dep[0]] = dep[1:]

            self.__get_relative(dep_map, root_id, ret_list)
        else:
            ret_list = departments

        return ret_list

    def getGroups(self, root_id):
        groups = self.database.execute(SQL.get_groups)

        if root_id:
            ret_list = []

            pos_map = {}
            for pos in groups:
                pos_map[pos[0]] = pos[1:]

            self.__get_relative(pos_map, root_id, ret_list)
        else:
            ret_list = groups

        return ret_list



    def getForm(self, form_sid, user_id, checksum):
        form = self.database.execute(SQL.get_form_by_sid % (form_sid))
        if not form:
            raise Exception (FBE_FORM_NOT_FOUND,'Active form with sid %s is not found!'%form_sid)

        ret_form_id = form_id = form[0][0]

        #get max form permission for current user
        form_perm = self.database.execute(SQL.get_form_perms % (form_id,user_id))

        if not form_perm:
            raise Exception (FBE_FORM_NOT_AUTHORIZED, 'User is not allow access to form')

        permission =  form_perm[0][0]

        #check form checksum
        ret = self.database.execute(SQL.check_form_checksum % (form_id, checksum))
        if ret:
            return (ret_form_id, '', permission)

        #get form source
        form = self.database.execute(SQL.get_form_source % form_id)

        form_source = str(form[0][0])

        return (ret_form_id, form_source, permission)


