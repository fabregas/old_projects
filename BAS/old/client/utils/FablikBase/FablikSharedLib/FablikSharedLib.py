import sql_fablik_lib as SQL
import thread
from Database import Database
import hashlib,uuid

class FablikBaseLibrary:
    def __init__(self, config_map):
        self.__lock = thread.allocate_lock()

        DATABASE_STRING = config_map.get('FB_DATABASE_STRING',None)
        DATABASE_PSWD = config_map.get('FB_DATABASE_PASSWORD',None)

        if DATABASE_STRING is None or DATABASE_PSWD is None:
            raise Exception('FB_DATABASE_STRING and FB_DATABASE_PASSWORD must be set for this cluster')

        self.database = Database( DATABASE_STRING % DATABASE_PSWD )

        self.syncronize(config_map)


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


    def syncronize(self, config):
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


    def __del__(self):
        if self.database:
            self.database.close()


    '''
    def authorize(self, session_id, role_sid):
        role = self.database.execute(SQL.authorize % )
    '''


    def authenticate(self, login, password):
        session_id = ''

        pwd = self.database.execute(SQL.get_password_hash % login)

        if not pwd:
            raise Exception(-1, 'User %s is not found!'%login)

        md5 = hashlib.md5()
        md5.update(password)
        pwd_hash = md5.hexdigest()

        if pwd_hash != pwd[0][0]:
            raise Exception (-2, 'Password is invalid')

        session_id = uuid.uuid4().hex
        
        user_id = pwd[0][1]
        session = self.database.execute(SQL.get_session % user_id)
        if session:
            self.database.modify(SQL.modify_session % (session_id, user_id))
            self.addAudit('user', user_id, 'repeatedLogin','')
        else:
            self.database.modify(SQL.insert_session % (session_id,user_id))

        return user_id, session_id

    def auth_by_session(self, session_id):
        session = self.database.execute(SQL.get_session_by_id % session_id)

        if not session:
            #self.addAudit('fablik', 0, 'invalidSession','') #TODO
            raise Exception('Session is not found!')

        return session[0]
        

    def getUserRoles(self, user_id):
        roles = self.database.execute(SQL.get_user_roles % user_id)

        return roles


    def addAudit(self, auditObject, auditObjectID, auditType, message):
        try:
            atype = self._get_audit_type(auditType, None)

            if atype is None:
                raise Exception("Audit type '%s' is not found" % auditType)

            (type_id, audit_level) = atype

            if self.audit_level < audit_level:
                return

            
            obj_type_id = self._get_object_type(auditObject, None)

            if obj_type_id is None:
                raise Exception("Audit object '%s' is not found" % auditObject)

            try:
                if auditObjectID is None:
                    auditObjectID = 0
                else:
                    auditObjectID = int(auditObjectID)
            except:
                raise Exception("Audit object ID id must be integer")


            try:
                message = str(message)
            except:
                raise Exception("Audit message be string")

            self.database.modify(SQL.insert_audit % (obj_type_id, auditObjectID, type_id, message))
        except Exception, msg:
            raise Exception(str(msg))


    def getMenus(self):
        menus = self.database.execute(SQL.get_menu)

        return menus

    def getInterfaces(self):
        urls = self.database.execute(SQL.get_interfaces)

        return urls

    def __get_relative(self, dep_map, root_id, ret_list):
        el = dep_map.get(root_id,None)

        if el is None:
            raise Exception('Root ID is not found')

        ret_list.append((root_id, el[0], el[1]))

        children = []
        for key in dep_map:
            if dep_map[key][0] == root_id:
                children.append(key)

        for item in children:
            self.__get_relative(dep_map, item, ret_list)


    def getDepartaments(self, root_id):
        departaments = self.database.execute(SQL.get_departaments)

        if root_id:
            ret_list = []

            dep_map = {}
            for dep in departaments:
                dep_map[dep[0]] = dep[1:]

            self.__get_relative(dep_map, root_id, ret_list)
        else:
            ret_list = departaments

        return ret_list

    def getPositions(self, root_id):
        positions = self.database.execute(SQL.get_positions)

        if root_id:
            ret_list = []

            pos_map = {}
            for pos in positions:
                pos_map[pos[0]] = pos[1:]

            self.__get_relative(pos_map, root_id, ret_list)
        else:
            ret_list = positions

        return ret_list

    def appendDepartament(self, parent_departament_id, name, description):
        if parent_departament_id is None:
            parent_departament_id = 'NULL'

        dep = self.database.execute(SQL.insert_departament % (parent_departament_id,name,description))
    
        return dep[0][0]

    def updateDepartament(self, departament_id, parent_id, name, description):
        self.database.modify(SQL.update_departament % (parent_id, name, description, departament_id))

    def deleteDepartament(self, departament_id):
        subdeps = self.database.execute(SQL.get_subdepartaments_count % departament_id)

        if subdeps[0][0] > 0:
            raise Exception('Departament contain subdepartaments!')

        self.database.modify(SQL.delete_deparatament % departament_id)

    def appendPosition(self, parent_position_id, name, description):
        if parent_position_id is None:
            parent_position_id = 'NULL'

        pos = self.database.execute(SQL.insert_position % (parent_position_id, name, description))

        return pos[0][0]

    def updatePosition(self, position_id, parent_id, name, description):
        self.database.modify(SQL.update_position % (parent_id, name, description, position_id))

    def deletePosition(self, position_id):
        subpositions = self.database.execute(SQL.get_subpositions_count % position_id)

        if subpositions[0][0] > 0:
            raise Exception('Position contain subpositions!')

        self.database.modify(SQL.delete_position % position_id)
