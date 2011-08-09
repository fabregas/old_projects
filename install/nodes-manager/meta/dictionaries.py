#!/usr/bin/python

from blik.utils.db_dict import DBDict
import sys

def basic_sync():
    try:
        #default users
        db_dict = DBDict('nm_user', ['id','name','password_hash','email_address','additional_info'], 'id')

        db_dict.add(id=1, name='admin', password_hash='26c01dbc175433723c0f3ad4d5812948',
                        email_address='blikproject@gmail.com', additional_info='')

        #roles
        db_dict = DBDict('nm_role', ['id','role_sid','role_name'], 'id')
        db_dict.add(1, 'admin', 'System administrator role')

        #default user roles
        db_dict = DBDict('nm_user_role', ['id', 'user_id','role_id'], 'id')
        db_dict.add(100000, 1, 1)
    except Exception, err:
        sys.stderr.write('Basic distionary synchronization failed! Details: %s'%err)
        return 1

    return 0


def synchronize_operations():
    try:
        db_dict = DBDict('nm_operation', ['id','name','timeout', 'node_type_id', 'description'], 'id')

        db_dict.add(1, 'SYNC', 10, None, 'Synchronization node parameters')
        db_dict.add(2, 'REBOOT', 10, None, 'Software node reboot')
        db_dict.add(3, 'GET_NODE_INFO', 10, None, 'Get actual information about node')
    except Exception, err:
        sys.stderr.write('Operations distionary synchronization failed! Details: %s'%err)
        return 1

    return 0


if __name__ == '__main__':
    ret = basic_sync()
    if ret:
        sys.exit(ret)

    ret = synchronize_operations()

    sys.exit(ret)
