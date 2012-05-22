#!/usr/bin/python
"""
Copyright (C) 2012 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.management.core
@author Konstantin Andrusenko
@date May 11, 2012
"""


from blik.utils.config import Config

from django.conf import settings

#setup databases settings for Django ORM
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': Config.db_host,
    'NAME': Config.db_name,
    'PASSWORD': Config.db_password,
    'PORT': Config.db_port,
    'USER': Config.db_user,
}

settings.configure()
settings.DATABASES = DATABASES


#---------------------------------------------------------------------

class Session:
    """
    Session class should has ability for user authorization
    Management API uses object of this class for determize
    permissions to its methods
    """
    def authorize(self, role):
        """
        This method check availibility of @role in user's roles list
        Return True if user has role and False if otherwise
        """
        raise RuntimeError('authorize method should be implemented in inherited class!')


class BaseManagementAPI:
    """
    This is base class for all management API
    """
    GLOBAL_SESSION = None

    @classmethod
    def init_global_session(cls, session):
        cls.GLOBAL_SESSION = session

    def __init__(self, session=None):
        if session is None:
            if self.GLOBAL_SESSION is None:
                raise Exception('User session does not found!')

            self.session = self.GLOBAL_SESSION
        else:
            self.session = session


def auth(role):
    def wraper(func):
         def dec_func(self, *args, **kvargs):
             if not self.session.authorize(role):
                 raise RuntimeError('Permission denied!')

             return  func(self, *args, **kvargs)
         return dec_func
    return wraper


