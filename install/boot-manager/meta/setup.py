from setuptools import setup
import sys
from version import VERSION

setup(
    name = "BootManager",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "kksstt@gmail.com",
    description = "Blik cloud boot manager",
    packages = ['blik', 'blik.bootManager'],  # include all packages under src
    scripts = ['bin/configureBootManager.py'],
    license = 'GPLv3',
    data_files = [('/etc/dhcp/', ['config/dhcpd.conf']),
                    ('/etc/bind', ['config/named.conf']),
                    ('/etc/bind/pri', ['config/blik.zone', 'config/192.168.87.zone'])],
    zip_safe = True
)

