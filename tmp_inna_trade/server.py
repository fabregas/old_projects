#!/usr/bin/python

import sys

import signal
from cherrypy import wsgiserver

import inna_trade.settings as cust_settings
from inna_trade.wsgi import application as app

#---------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8888), app)

    def stop_handler(sig, arg):
        server.stop()

    signal.signal(signal.SIGINT, stop_handler)

    try:
         server.start()
    except Exception, err:
         print 'ERROR: %s'%err
         try:
             stop_handler(0,0)
         except Exception, err:
	     print 'stop error: %s'%err
#---------------------------------------------------------------------------------------------------------

