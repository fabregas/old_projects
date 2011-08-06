from databaseConnection import DatabaseConnection

class DBDict:
    def __init__(self, dict_name, dict_fields, unique_field):
        self.name = dict_name
        self.fields = dict_fields
        self.unique_field = unique_field
        self.dbconn = DatabaseConnection()

        try:
            self.fields.index(unique_field)
        except ValueError, err:
            raise Exception('Unique field %s is not found in dict fields!'%unique_field)

    def add(self, *k_params, **params):
        if k_params:
            if len(k_params) != len(self.fields):
                raise Exception('Parameters couns invalid! Expected %s items'%len(self.fields))

            params = {}
            for i,param_name in enumerate(self.fields):
                params[param_name] = k_params[i]
        #check params
        for param in params:
            try:
                self.fields.index(param)
            except ValueError, err:
                raise Exception('Parameter %s is not defined as dict fields!'%param)

        for param in self.fields:
            if not params.has_key(param):
                raise Exception('Parameter %s is expected for this dict!'%param)


        if self._has_dict_item(params[self.unique_field]):
            self._update_dict_item(params)
        else:
            self._insert_dict_item(params)


    def _has_dict_item(self, unique_value):
        #select unique value from dict
        query = 'SELECT %s FROM %s WHERE %s'%(self.unique_field, self.name, self.unique_field+'=%s')

        rows = self.dbconn.select(query, (unique_value,))

        if rows:
            return True
        else:
            return False

    def _update_dict_item(self, params):
        set_strs = []
        set_values = []

        for param, value in params.items():
            set_strs.append(param + '=%s')
            set_values.append(value)

        set_str = ', '.join(set_strs)

        query = "UPDATE %s SET %s WHERE %s='%s'"%(self.name, set_str,
            self.unique_field, params[self.unique_field])

        self.dbconn.modify(query, set_values)

    def _insert_dict_item(self, params):
        fields_str = ', '.join(params)
        values_map = ', '.join(['%s' for i in params])

        query = 'INSERT INTO %s (%s) VALUES (%s)'%(self.name, fields_str, values_map)

        self.dbconn.modify(query, params.values())


'''
#USAGE EXAMPLE:

try:
    dbdict = DBDict('nm_operation', ['name', 'timeout', 'node_type_id','description'], 'name')

    dbdict.add(name='TEST', timeout=122, node_type_id=None, description='test operation')
    dbdict.add(name='TEST', timeout=302, node_type_id=1, description='->mod<- test operation')
    dbdict.add('TEST2', 10, 1, '>>>test operation #2',5)
except Exception, err:
    print 'ERROR: %s'%err
'''
