import json
import os
from settings import MENU_DIR

#menu item fields
MF_PARENT_ID = 'parent_id'
MF_SID = 'sid'
MF_ROLE = 'role'
MF_LABEL = 'label'
MF_URL = 'url'
MF_CHILDREN = 'children'

def _parse_menu_file(menu_file):
    try:
        menu_file = open(menu_file)
    except Exception, err:
        raise Exception('Error while try opening %s file' % menu_file)


    try:
        menu = json.load(menu_file)
    except Exception, err:
        raise Exception('Error while try parsing %s file' % menu_file)

    return menu


def _load_menu_files():
    menu = {}
    files = os.listdir(MENU_DIR)

    for item in files:
        f_item = os.path.join(MENU_DIR, item)
        if (not os.path.isfile(f_item)) or (not item.endswith('.json')):
            continue

        menu_part = _parse_menu_file(f_item)
        menu.update(menu_part)

    return menu

def _validate_menu_item(item_id, item):
    try:
        int(item_id)
    except:
        raise Exception('Menu item ID should be integer, but "%s"'%item_id)

    if not item.has_key(MF_PARENT_ID):
        raise Exception('Menu item with ID %s is not contain parent_id attribute'%item_id)
    if not item.has_key(MF_SID):
        raise Exception('Menu item with ID %s is not contain sid attribute'%item_id)
    if not item.has_key(MF_ROLE):
        raise Exception('Menu item with ID %s is not contain role attribute'%item_id)
    if not item.has_key(MF_LABEL):
        raise Exception('Menu item with ID %s is not contain label attribute'%item_id)
    if not item.has_key(MF_URL):
        raise Exception('Menu item with ID %s is not contain url attribute'%item_id)

    if item[MF_ROLE].lower() == 'none':
        item[MF_ROLE] = None

    if item[MF_PARENT_ID].lower() == 'none':
        item[MF_PARENT_ID] = None
    else:
        try:
            int(item[MF_PARENT_ID])
        except:
            raise Exception('Menu item with ID %s contain invalid parent_id attribute'%item_id)

    item[MF_CHILDREN] = []


def get_menu():
    '''
    get menu structure.
    appending 'children' attribute to every menu item - list of children menu items
    '''
    menu = _load_menu_files()

    for key, value in menu.items():
        _validate_menu_item(key, value)

    for key, value in menu.items():
        if value[MF_PARENT_ID] is None:
            continue

        parent_id = value[MF_PARENT_ID]
        menu[parent_id][MF_CHILDREN].append((key, value))

    for key, value in menu.items():
        if not value[MF_CHILDREN]:
            continue

        value[MF_CHILDREN].sort(lambda a, b: cmp(a[0], b[0]))
        value[MF_CHILDREN] = [i[1] for i in value[MF_CHILDREN]]

    ret_menu = []
    for key, value in menu.items():
        if value[MF_PARENT_ID] is None:
            ret_menu.append((key,value))

    ret_menu.sort(lambda a, b: cmp(a[0], b[0]))
    return [i[1] for i in ret_menu]

