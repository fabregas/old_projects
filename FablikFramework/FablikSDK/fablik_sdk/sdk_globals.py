
import os

SDK_VERSION = "1.0"

HOME = '/home/fabregas' #FIXME!!!
SDK_CONF = ".fablik_sdk"
CLIENT_LIB = 'FablikClientLib'

PYUI_BIN = '/usr/bin/pyuic4'

WIDGET_FILE     = "FormWidget.py"
PYFORM_FILE     = "Form.py"
UIFORM_FILE     = "form.ui"
CONT_FILE       = "content.xml"

UI_TEMPLATE     = os.path.join(HOME,"form.ui")

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

