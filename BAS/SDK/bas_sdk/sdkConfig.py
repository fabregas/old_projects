
import os
from xml.etree.ElementTree import ElementTree, Element, SubElement
from bas_sdk_globals import *

class ApplicationServer:
    def __init__(self, name='', url='', login='', password=''):
        self.url = url
        self.login = login
        self.password = password
        self.name = name


class Config:
    def __init__(self, conf_file):
        self.file_path = conf_file
        self.app_servers = []

        self._load()
    
    def _new(self):
        conf_e = Element('config')
        conf_e.append(Element('app_servers'))
        
        self.dom = ElementTree(conf_e)
        self.dom.write(self.file_path)


    def _load(self):
        if not os.path.exists(self.file_path):
            return self._new()

        self.dom = ElementTree()
        self.dom.parse(self.file_path)

        conf_e = self.dom.getroot()

        if conf_e.tag != 'config':
            raise Exception('<config> tag expected!')

        for node in list(conf_e):
            if node.tag == 'app_servers':
                self.app_servers = self.__get_app_servers(node)


    def __get_app_servers(self, rootNode):
        servers = []

        for node in list(rootNode):
            if node.tag == 'server':
                appServer = ApplicationServer()

                for node in node:
                    if node.text is None:
                        node.text = ''

                    if node.tag == 'name':
                        appServer.name = node.text.strip()
                    elif node.tag == 'url':
                        appServer.url = node.text.strip()
                    elif node.tag == 'login':
                        appServer.login = node.text.strip()
                    elif node.tag == 'password':
                        appServer.password = node.text.strip()

                servers.append(appServer)

        return servers

    def save(self):
        self._new()
        servs_e = self.dom.find('app_servers')

        for server in self.app_servers:
            serv = SubElement(servs_e, 'server')

            node = SubElement(serv, 'name')
            node.text = server.name
            node = SubElement(serv, 'url')
            node.text = server.url
            node = SubElement(serv, 'login')
            node.text = server.login
            node = SubElement(serv, 'password')
            node.text = server.password

        smart_xml_ident(self.dom.getroot())
        self.dom.write(self.file_path)
