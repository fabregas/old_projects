from WSGI import SoapApplication
import os

SYNC_FILE = '/tmp/sync_app.tmp'
START_FILE = '/tmp/start_app.tmp'

class Application(SoapApplication):
    def start(self, config):
        ''' init routine for web service'''
        s = ''
        for key in config:
            s += '%s = %s\n' %(key, config[key])

        open(START_FILE,'w').write(s)

    def synchronize(self, config):
        '''synchronize application cache and configuration'''
        s = ''
        for key in config:
            s += '%s = %s\n' %(key, config[key])

        open(SYNC_FILE,'w').write(s)

    def stop(self):
        '''destroy routine for web service'''
        if os.path.exists(SYNC_FILE):
            os.remove(SYNC_FILE)

        os.remove(START_FILE)

