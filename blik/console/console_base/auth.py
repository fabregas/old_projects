# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import hashlib
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _

from blik.utils.databaseConnection import DatabaseConnection

class User:
    def __init__(self, login, md5_pwd, roles=[]):
        self.username = username
        self.md5_password = md5_pwd
        self.roles = roles


SESSION_KEY = '_auth_user_id'

USERS_CACHE = {} #key=user login, value=object of User class

def update_user_cache(user_id):
    global USERS_CACHE

    user = dbconn.select("SELECT id, name, password_hash FROM nm_user WHERE id=%s", (user_id,))

    user_id, user_name, user_pwd = user
    roles = dbconn.select("SELECT R.role_sid FROM nm_role R, nm_user_role UR \
                            WHERE UR.role_id=R.id AND UR.user_id=%s", (user_id,))
    roles = [r[0] for r in roles]

    USERS_CACHE[user_name] = User(user_name, user_pwd, roles)

def cache_users():
    '''
    Flush users memory cache and read users and its roles from database.
    '''
    global USERS_CACHE
    USERS_CACHE = {}

    dbconn = DatabaseConnection()
    users = dbconn.select("SELECT id, name, password_hash FROM nm_user")

    for user in users:
        user_id, user_name, user_pwd = user

        roles = dbconn.select("SELECT R.role_sid FROM nm_role R, nm_user_role UR \
                                WHERE UR.role_id=R.id AND UR.user_id=%s", (user_id,))
        roles = [r[0] for r in roles]

        USERS_CACHE[user_name] = User(user_name, user_pwd, roles)


def authenticate(username, password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf8'))
    passwd = md5.hexdigest()

    user = USERS_CACHE.get(username, None)

    if not user:
        raise Exception('User with login "%s" is not found!'%username)

    if user.md5_password != passwd:
        raise Exception('Password is invalid!')

    return user

def is_authorize(request, role_sid):
    user_login = request.session.get(SESSION_KEY, None)

    if not user_login:
        raise Exception ('User is not authenticate!')

    user = USERS_CACHE[user_login]

    if str(role_sid) in user.roles:
        return True

    return False



def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """

    request.session[SESSION_KEY] = user.username


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    request.session.flush()


def is_authenticated(request):
    return request.session.get(SESSION_KEY, False)


def get_current_user(request):
    user_login = request.session.get(SESSION_KEY, None)

    if not user_login:
        return None

    return USERS_CACHE[user_login]


