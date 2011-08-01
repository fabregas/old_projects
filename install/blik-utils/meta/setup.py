from setuptools import setup
import sys
from version import VERSION

setup(
    name = "BlikUtils",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "blikproject@gmail.com",
    description = "Blik utilities for BlikCloud system",
    packages = ['blik.utils'],  # include all packages under src
    license = 'GPLv3',
    zip_safe = True
)

