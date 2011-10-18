# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import hashlib
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _
from models import NmUser, NmUserRole
from forms import AuthForm


SESSION_KEY = '_auth_user_id'

USERS_CACHE = {} #key=user login, value=object of NmUser class

def update_user_cache(user):
    global USERS_CACHE

    roles = NmUserRole.objects.filter(user=user)

    user.roles = [r.role_sid for r in roles]

    USERS_CACHE[user.name] = user


def cache_users():
    '''
    Flush users memory cache and read users and its roles from database.
    '''
    global USERS_CACHE
    USERS_CACHE = {}

    users = NmUser.objects.all()

    for user in users:
        update_user_cache(user)


def authenticate(username, password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf8'))
    passwd = md5.hexdigest()

    user = USERS_CACHE.get(username, None)

    if not user:
        raise Exception('User with login "%s" is not found!'%username)

    if user.password_hash != passwd:
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

    request.session[SESSION_KEY] = user.name


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


#--------------------------------------------------------------------------------------------------
# AUTH views
#--------------------------------------------------------------------------------------------------

def authenticate_user(request):
    user = None
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            passwd = form.cleaned_data['passwd']

            try:
                user = authenticate(username=username, password=passwd)
            except Exception, err:
                form.error = err
            else:
                login(request, user)
                return HttpResponseRedirect('/')
    else:
        form = AuthForm()

    return render_to_response('auth.html',{'form':form})


