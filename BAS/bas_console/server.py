
import wsgiserver
import sys
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings
import signal

class DjangoApplication(WSGIHandler):
    def __init__(self):
        WSGIHandler.__init__(self)

        import settings as cust_settings

        settings.configure(cust_settings)

#---------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app = DjangoApplication()

    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 80), app, maxthreads=10)

    def stop_handler(sig, arg):
        server.stop()

    signal.signal(signal.SIGINT, stop_handler)

    server.start()

#---------------------------------------------------------------------------------------------------------

