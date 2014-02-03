
from bas_sdk_globals import *
import os, sys
from xml.etree.ElementTree import ElementTree, Element
from sdkProject import SDKProject
from replace_tabs import replace


SIMPLE_TYPES = {'string': 'simple.String', 'integer':'simple.Integer', 'binary':'binary.Attachment'}


class Parameter:
    def __init__(self, name='', ptype=''):
        self.name = name
        self.ptype = ptype

        self.children = []

    def generate_code(self, intend=''):
        s = ''
        if self.ptype == 'complex':
            s += '%sclass %s(ClassSerializer):\n'%(intend,self.name)

            for child in self.children:
                s += child.generate_code(intend+'\t')
        elif self.ptype.lower() == 'list':
            item_type = SIMPLE_TYPES.get(self.item_type.lower(), self.item_type)
            s += "%s%s = simple.Array(%s, '%s', '%sArray')\n" % (intend, self.name, item_type, self.item_name, self.name)
        else:
            imp_type = SIMPLE_TYPES.get(self.ptype.lower(), self.ptype)

            s += '%s%s = %s\n'%(intend,self.name,imp_type)

        return s


    def from_node(self, rootNode):
        self.name = rootNode.get('name').strip()
        self.ptype = rootNode.get('type','').strip()
        if self.ptype == '' and len(list(rootNode)) > 0:
            self.ptype = 'complex'

        if self.ptype.lower() == 'list':
            self.item_name = rootNode.get('item_name','item').strip()
            self.item_type = rootNode.get('item_type','string').strip()

        if self.ptype != 'complex':
            return self

        for node in list(rootNode):
            if node.tag == 'parameter':
                param = Parameter().from_node(node)
                self.children.append(param)

        return self

class TypeDef:
    def __init__(self, name=''):
        self.name = name
        self.typeName = name
        self.parameters = []

    def generate_code(self, intend=''):
        s = '%sclass %s(ClassSerializer):\n'%(intend,self.typeName)

        for param in self.parameters:
            s += param.generate_code(intend+'\t')

        return s

    def from_node(self, rootNode, name=''):
        self.typeName = rootNode.get('name').strip()

        for node in list(rootNode):
            if node.tag == 'parameter':
                param = Parameter().from_node(node)
                self.parameters.append(param)

        return self

class Message(TypeDef):
    def from_node(self, rootNode, name=''):
        self.name = rootNode.get('name','').strip()
        if not self.name  and not name:
            raise Exception('Message name is not found!')

        if not self.name:
            self.name = name

        self.typeName = rootNode.get('typeName','').strip()
        if not self.typeName:
            self.typeName = self.name[0].upper() + self.name[1:]
    
        for node in list(rootNode):
            if node.tag == 'parameter':
                param = Parameter().from_node(node)
                self.parameters.append(param)

        return self


class Method:
    def __init__(self, name='', is_async=False, inputMessage=None, outputMessage=None):
        self.name = name
        self.is_async = is_async
        self.inputMessage = inputMessage
        self.outputMessage = outputMessage


    def generate_code(self, intend=''):
        s = ''
        if not self.is_async:
            ret = ''
            if self.outputMessage:
                ret = ", _returns = %s(), _outVariableName='%s'" % (self.outputMessage.typeName,self.outputMessage.name)

            s += '\n%s@soapmethod( %s %s )\n'%(intend,self.inputMessage.typeName, ret)

            s += '%sdef %s(self, %s):\n'%(intend,self.name, self.inputMessage.name)
            s += '%s\treturn self.__implementation.%s(%s)\n'%(intend, self.name, self.inputMessage.name)
        else:
            s += '\n%s@soapmethod( %s, _isAsync=True)\n'%(intend,self.inputMessage.typeName)
            s += '%sdef %s(self, %s):\n'%(intend,self.name, self.inputMessage.name)

            s += '%s\tmsgid, replyto = get_callback_info()\n'%(intend)
            s += '%s\tdef run():\n'%(intend)
            s += '%s\t\ttry:\n'%(intend)
            s += '%s\t\t\toutputVariable = self.__implementation.%s( %s )\n'%(intend, self.name,self.inputMessage.name)
            s += '%s\t\t\tclient = make_service_client(replyto, self)\n'%(intend)
            s += '%s\t\t\tclient.%sCallback(outputVariable, msgid=msgid)\n'%(intend, self.name)
            s += '%s\t\texcept:\n'%(intend)
            s += '%s\t\t\tself.onException({"HTTP_SOAPACTION":"%s"}, "ASYNC METHOD EXCEPTION", get_stacktrace())\n'%(intend,self.name)
            s += '%s\tAsyncWorkQueue.put(run)\n'%(intend)


            s += '\n%s@soapmethod( %s , _isCallback=True)\n'%(intend,self.outputMessage.typeName)
            s += '%sdef %sCallback(self, %s):\n'%(intend,self.name, self.outputMessage.name)
            s += '%s\tpass\n'%(intend)

        return s

    def from_node(self, rootNode):
        self.name = rootNode.get('name').strip()

        self.is_async = False
        attr = rootNode.get('is_async')
        if attr and attr.lower() == 'true':
            self.is_async = True

        upperName = self.name[0].upper() + self.name[1:]
        for node in list(rootNode):
            if node.tag == 'input':
                self.inputMessage = Message().from_node(node, 'request%s'%upperName)
            elif node.tag == 'output':
                self.outputMessage = Message().from_node(node, 'response%s'%upperName)


        return self



class ApplicationInterface:
    def __init__(self, app_path):
        self.file_path = os.path.join(app_path, IFACE_FILE)
        self.app_path = app_path

        sdk_proj = SDKProject(os.path.join(app_path, PROJ_FILE))
        self.name = sdk_proj.name

        self.methods = []
        self.types = []

        self.__parse()

    def generate_application(self):
        s = 'from %s import *\n' % TYPES_FILE[:-3]
        s += 'import %s\n' % ROUTINES_FILE[:-3]
        s += 'import WSGI\n'
        s += 'import soaplib\n'
        s += 'from soaplib.util import get_callback_info, get_stacktrace\n'
        s += 'from soaplib.client import make_service_client\n'
        s += 'from AsyncWorkManager import AsyncWorkQueue\n'
        s += 'from WSGI import soapmethod\n\n\n'

        s += 'class %s ( WSGI.SoapApplication ):\n' % self.name
        s += "\tdef start(self, config={}):\n\t\t''' init routine for web service'''\n"
        s += '\t\tself.__implementation = %s.%sImplementation()\n'%(ROUTINES_FILE[:-3], self.name)
        s += '\t\tself.__implementation.start_routine(config)\n'
        s += "\n\tdef synchronize(self, config):\n\t\t'''synchronize application cache and configuration'''\n\t\tself.__implementation.synchronize(config)\n"
        s += "\n\tdef stop(self):\n\t\t'''destroy routine for web service'''\n\t\tself.__implementation.stop_routine()\n"

        for method in self.methods:
            s += method.generate_code('\t')
            s += '\n'

        f = open(os.path.join(self.app_path, APP_FILE),'w')
        f.write(replace(s))
        f.close()

    def generate_types(self):
        s  = 'import soaplib\n'
        s += 'from soaplib.serializers.clazz import ClassSerializer\n'
        s += 'import soaplib.serializers.primitive as simple\n'
        s += 'import soaplib.serializers.binary as binary\n\n'

        for typedef in self.types:
            s += typedef.generate_code()
            s += '\n'

        for method in self.methods:
            if method.inputMessage:
                s += method.inputMessage.generate_code()
                s += "\n"
            if method.outputMessage:
                s += method.outputMessage.generate_code()
                s += "\n"

        f = open(os.path.join(self.app_path, TYPES_FILE),'w')
        f.write(replace(s))
        f.close()


    def generate_routines(self):
        s  = 'import %s as IO\n\n' % TYPES_FILE[:-3]
        s += 'class %sImplementation:\n' % self.name
        s += '\tdef start_routine(self, config):\n\t\tpass\n\n'
        s += '\tdef synchronize(self, config):\n\t\tpass\n\n'
        s += '\tdef stop_routine(self):\n\t\tpass\n\n'

        for method in self.methods:
            s += '\tdef %s(self, request):\n'% method.name
            if method.inputMessage:
                s += "\t\t#request - object of IO.%s\n" % method.inputMessage.typeName
            else:
                s += "\t\t#request - None object \n"

            if method.outputMessage:
                s += '\t\t#response - object of IO.%s\n' % method.outputMessage.typeName
            else:
                s += '\t\t#response - None object\n' 
            s += '\n\t\tpass\n\n'

        fname = os.path.join(self.app_path, ROUTINES_FILE)
        if os.path.exists(fname):
            sys.stdout.write('Warning: File %s is already exists. Write to %s.new\n' % (fname,fname))
            fname +=  '.new'

        f = open(fname,'w')
        f.write(replace(s))
        f.close()

    def generate_init(self):
        fname = os.path.join(self.app_path, '__init__.py')

        f = open(fname, 'w')
        f.write('from Application import %s as %s'%(self.name,'Application'))
        f.close()

    def generate_tests(self):
        s  = 'import unittest\n'
        s += 'import %s as types\n' % TYPES_FILE[:-3]
        s += 'from %s import *\n\n\n' % ROUTINES_FILE[:-3]
        s += 'class Test%s(unittest.TestCase):\n'%self.name

        for method in self.methods:
            s += '\tdef test_%s(self):\n' % method.name
            s += '\t\t#write code for testing %s routine\n\n'% method.name
            s += '\t\tpass\n\n'


        fname = os.path.join(self.app_path, TEST_FILE)
        if os.path.exists(fname):
            sys.stdout.write('Warning: File %s is already exists. Write to %s.new\n' % (fname,fname))
            fname += '.new'

        f = open(fname,'w')
        f.write(replace(s))
        f.close()


    def __parse_methods(self, node):
        for node in list(node):
            if node.tag == 'method':
                method = Method().from_node(node)
                self.methods.append(method)

    def __parse_types(self, node):
        for node in list(node):
            if node.tag == 'type':
                typedef = TypeDef().from_node(node)
                self.types.append(typedef)

    def __parse(self):
        self.dom = ElementTree()
        self.dom.parse(self.file_path)

        iface_e = self.dom.getroot()

        if iface_e.tag != 'interface':
            raise Exception('<interface> tag expected!')


        for node in list(iface_e):
            if node.tag == 'types':
                self.__parse_types(node)

        for node in list(iface_e):
            if node.tag == 'methods':
                self.__parse_methods(node)



