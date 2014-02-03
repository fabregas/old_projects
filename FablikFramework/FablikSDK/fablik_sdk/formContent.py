
import os, sys
from xml.etree.ElementTree import ElementTree, Element
from sdk_globals import *


class FormContent:
    def __init__(self, prj_path):
        self.file_path = prj_path

        self.name = None
        self.files = []

        self.dom = None
        self._load()

    def getLangFiles(self):
        return self.langs

    def appendLangFile(self, lang_sid, lang_file):
        del_idx = None
        for i,(l_sid,l_file) in enumerate(self.langs):
            if l_sid == lang_sid and l_file == lang_file:
                return
            if l_sid == lang_sid and l_file != lang_file:
                del_idx = i

        if del_idx is not None:
            del self.langs[del_idx]

        self.langs.append((lang_sid,lang_file))

    def getFiles(self):
        return self.files

    def setName(self, project_name):
        self.name = project_name

    def appendFiles(self, files):
        if not issubclass(files.__class__, [].__class__):
            raise Exception ('appendFiles method expect list as input')

        for (f_mod,f_name) in files:
            is_append = True
            for (ff_mod, ff_name) in self.files:
                if ff_mod == f_mod and ff_name == f_name:
                    is_append = False
                    break
            if is_append:
                self.files.append((f_mod, f_name))

    def __validate(self):
        if self.name == None:
            raise Exception ("Name is not found!")

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
            elif node.tag == 'files':
                self.files = self.__get_files(node)
        self.__validate()


    def save(self):
        self.__validate()

        proj_e = self.dom.getroot()

        for node in list(proj_e):
            if node.tag == 'name':
                node.text = self.name
            elif node.tag == 'files':
                self.__set_files(node)

        smart_xml_ident(self.dom.getroot())
        self.dom.write(self.file_path)
