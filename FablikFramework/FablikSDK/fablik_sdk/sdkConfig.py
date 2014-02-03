
import os
from xml.etree.ElementTree import ElementTree, Element, SubElement
from sdk_globals import *


class Config:
    def __init__(self, conf_file):
        self.file_path = conf_file
        self.db_conn_strings = {}
        self.lib_path = '.'
        self.user = ''
        self.password = ''

        self._load()

    def _new(self):
        conf_e = Element('config')
        conf_e.append(Element('databases'))
        conf_e.append(Element('fablikClient', {'libPath':self.lib_path,'user':self.user,'password':self.password}))

        self.dom = ElementTree(conf_e)
        self.dom.write(self.file_path)

    def get_username(self):
        return self.user

    def get_password(self):
        return self.password

    def get_lib_path(self):
        return self.lib_path

    def set_lib_path(self, lib_path):
        self.lib_path = lib_path

    def get_db_connections(self):
        return self.db_conn_strings

    def get_connect_string(self, name):
        return self.db_conn_strings.get(name,None)

    def append_db_connection(self, conn_name, conn_string):
        self.db_conn_strings[conn_name] = conn_string

    def remove_db_connection(self, conn_name):
        if not self.db_conn_string.has_key(conn_name):
            return -1

        del self.db_conn_string[conn_name]

        return 0

    def _load(self):
        if not os.path.exists(self.file_path):
            return self._new()

        self.dom = ElementTree()
        self.dom.parse(self.file_path)

        conf_e = self.dom.getroot()

        if conf_e.tag != 'config':
            raise Exception('<config> tag expected!')

        for node in list(conf_e):
            if node.tag == 'databases':
                self.db_conn_strings = self.__get_db_connect_strings(node)
            elif node.tag == 'fablikClient':
                self.lib_path = node.get('libPath')
                self.user = node.get('user')
                self.password = node.get('password')


    def __get_db_connect_strings(self, rootNode):
        connects = {}

        for node in list(rootNode):
            if node.tag == 'db_connect_string':
                attr = node.get('name')
                if not attr:
                    raise Exception('Attribute name is must be in db_connect_string tag!')

                connects[attr.strip()] =  node.text.strip()

        return connects

    def save(self):
        self._new()
        dbs_e = self.dom.find('databases')

        for conn_name in self.db_conn_strings:
            node = SubElement(dbs_e, 'db_connect_string', {'name':conn_name})
            node.text = self.db_conn_strings[conn_name]

        smart_xml_ident(self.dom.getroot())
        self.dom.write(self.file_path)
