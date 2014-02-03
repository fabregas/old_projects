# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from forms import AuthForm
from models import RPUser, RPMessage
import hashlib
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _


SESSION_KEY = '_auth_user_id'

def authenticate(username, password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf8'))
    passwd = md5.hexdigest()

    users = RPUser.objects.filter(login=username, password_md5=passwd)
    if len(users) != 1:
        return None

    user = users[0]

    return user

def is_authorize(request, role_sid):
    user_id = request.session.get(SESSION_KEY,None)

    if not user_id:
        raise Exception ('User is not authenticate!')

    user = RPUser.objects.get(id=user_id)

    if str(user.role) == str(role_sid):
        return True
    return False



def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """

    request.session[SESSION_KEY] = user.id


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    request.session.flush()

def is_authenticated(request):
    return request.session.get(SESSION_KEY, False)

def get_current_user(request):
    user_id = request.session.get(SESSION_KEY,None)

    if not user_id:
        return None

    user = RPUser.objects.get(id=user_id)

    if user.role == 'admin':
        user.has_messages = RPMessage.objects.filter(binded_user=None, is_readed=0)
    else:
        user.has_messages = RPMessage.objects.filter(binded_user=user, is_readed=0)

    return user


def auth_user(request):
    error = None
    form = None
    user = None

    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            passwd = form.cleaned_data['passwd']

            user = authenticate(username=username, password=passwd)
            if user is not None:
                login(request, user)
            else:
                form.error = _(u"Ви ввели невірний логін або пароль!")
    else:
        form = AuthForm()

    user = get_current_user(request)

    return form, user


