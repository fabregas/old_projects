
import sys
import os
import platform

dist = platform.dist()[0].lower()

try:
    import gst
    need_gst = False
except ImportError:
    need_gst = True

try:
    import soundcloud
    need_soundcloud = False
except ImportError:
    need_soundcloud = True


if need_soundcloud:
    ret = os.system('easy_install soundcloud')
    if not ret:
        sys.stderr.write('ERROR: soundcloud package does not installed!\n')
        sys.exit(1)

if need_gst:
    if dist == 'ubuntu':
        ret = os.system('atp-get install python-gst0.10')
        if ret:
            sys.stderr.write('ERROR: python-gst0.10 does not installed!\n')
            sys.exit(1)
    else:
        print '='*80
        print 'WARNING! You should setup python-gst manually for your distributive'
        print '='*80

if not os.path.exists('/opt/blik/sc_player'):
    os.makedirs('/opt/blik/sc_player/')
os.system('cp sc_player /opt/blik/sc_player/')
os.system('chmod +x /opt/blik/sc_player/sc_player')

print '\nRun /opt/blik/sc_player/sc_player for starting player ;)\n'
