

SDK_VERSION = "1.0"

HOME = '/home/fabregas' #FIXME!!!
SDK_CONF = ".bas_sdk"
SYS_LIB = 'BASLibraries'
USER_LIB = 'UserLibraries'


APP_FILE        = "Application.py"
TYPES_FILE      = "IOTypesStructure.py"
ROUTINES_FILE   = "ApplicationImplementation.py"
PROJ_FILE       = "project.prj"
IFACE_FILE      = "interface.wsi"
TEST_FILE       = "tests.py"



def smart_xml_ident(root, level=0):
        i = '\n' + level*'\t' 
        if len(root):
            if not root.text or not root.text.strip():
                root.text = i + '\t'
            if not root.tail or not root.tail.strip():
                root.tail = i

            last = None
            for elem in list(root):
                smart_xml_ident(elem, level+1)
                last = elem

            if last is not None:
                last.tail = last.tail[:-1]

            if not root.tail or not root.tail.strip():
                root.tail = i
        else:
            if level and (not root.tail or not root.tail.strip()):
                root.tail = i

