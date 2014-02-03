import ConfigParser
from errorMessages import MESSAGES

class LangConfig:
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read([config_file])

    def getLanguage(self, lang_sid):
        try:
            name = self.config.get(lang_sid, 'Name',None)
            filename = self.config.get(lang_sid, 'TranslateFile',None)
        except Exception, err:
            raise Exception(MESSAGES.get(105,'Config file corrupted!'))

        return (name,filename)

    def getLanguages(self):
        sects = self.config.sections()

        ret_map = {}
        try:
            for id,sect in enumerate(sects):
                name = self.config.get(sect, 'Name',None)
                ret_map[id] = (sect, unicode(name.decode('utf8')))
        except Exception, err:
            print err
            raise Exception(MESSAGES.get(105,'Config file corrupted!'))

        return ret_map
