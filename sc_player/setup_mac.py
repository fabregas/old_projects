from setuptools import setup
import sys
import subprocess


APP = ['sc_player']
OPTIONS = {'argv_emulation': False,
           'compressed' : 'True',
          }

setup(
    name= 'sc_player',
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
