
import os, sys
from xml.etree.ElementTree import ElementTree, Element
from bas_sdk_globals import *


class SDKProject:
    def __init__(self, prj_path):
        self.file_path = prj_path

        self.name = None
        self.author = None
        self.pythonVersion = None
        self.clientVersion = None
        self.files = []

        self.dom = None
        self._load()

    def getFiles(self):
        return self.files

    def setName(self, project_name):
        self.name = project_name

    def setAuthor(self, author):
        self.author = author
    
    def setPythonVersion(self, version=None):
        if not version:
            v = sys.version_info
            version = "%i.%i.%i" % (v[0],v[1],v[2])
            
        self.pythonVersion = version

    def setClientVersion(self, version):
        self.clientVersion = version

    def appendFiles(self, files):
        if not issubclass(files.__class__, [].__class__):
            raise Exception ('appendFiles method expect list as input')

        self.files += files

    def __validate(self):
        if self.name == None:
            raise Exception ("Name is not found!")
        if self.author == None:
            raise Exception ("Author is not found!")
        if self.pythonVersion == None:
            raise Exception ("PythonVersion is not found!")
        if self.clientVersion == None:
            raise Exception ("ClientVersion is not found!")


    def __get_files(self, rootNode):
        files = []

        for node in list(rootNode):
            if node.tag == 'file':
                file_path = node.text.strip()

                attr = node.get('module')
                if attr:
                    file_module = attr.strip()
                else:
                    file_module = os.path.basename(file_path).split('.')[0]
        
                files.append((file_module, file_path))

        return files

    def __set_files(self, rootNode):
        rootNode.clear()

        for (f_mod,f_name) in self.files:
            subitem = Element('file',{'module':f_mod})
            subitem.text = f_name

            rootNode.append(subitem)
            


    def _new(self):
        proj_e = Element('project')
        proj_e.append(Element('name'))
        proj_e.append(Element('author'))
        proj_e.append(Element('python_version'))
        proj_e.append(Element('client_version'))
        proj_e.append(Element('files'))
        
        self.dom = ElementTree(proj_e)

        self.dom.write(self.file_path)


    def _load(self):
        if not os.path.exists(self.file_path):
            return self._new()
            
        self.dom = ElementTree()
        self.dom.parse(self.file_path)

        proj_e = self.dom.getroot()

        if proj_e.tag != 'project':
            raise Exception('<project> tag expected!')

        for node in list(proj_e):
            if node.text == None:
                node.text = ''
            if node.tag == 'name':
                self.name = node.text.strip()
            elif node.tag == 'author':
                self.author = node.text.strip()
            elif node.tag == 'python_version':
                self.pythonVersion = node.text.strip()
            elif node.tag == 'client_version':
                self.clientVersion = node.text.strip()
            elif node.tag == 'files':
                self.files = self.__get_files(node)
        self.__validate()


    def save(self):
        self.__validate()

        proj_e = self.dom.getroot()

        for node in list(proj_e):
            if node.tag == 'name':
                node.text = self.name
            elif node.tag == 'author':
                node.text = self.author
            elif node.tag == 'python_version':
                node.text = self.pythonVersion
            elif node.tag == 'client_version':
                node.text = self.clientVersion
            elif node.tag == 'files':
                self.__set_files(node)
        

        smart_xml_ident(self.dom.getroot())
        self.dom.write(self.file_path)
