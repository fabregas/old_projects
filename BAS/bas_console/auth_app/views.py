# Create your views here.

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from forms import AuthForm
from console.models import BasUser,BasUserRoles,BasRole
import hashlib
from django.contrib.auth.models import AnonymousUser


SESSION_KEY = '_auth_user_id'

def authenticate(username, password):
    md5 = hashlib.md5()
    md5.update(password)
    passwd = md5.hexdigest()

    users = BasUser.objects.filter(name=username, password_md5=passwd)
    if len(users) != 1:
        return None

    user = users[0]

    return user

def is_authorize(request, role_sid):
    user_id = request.session.get(SESSION_KEY,None)

    if not user_id:
        raise Exception ('User is not authenticate!')

    role = BasRole.objects.filter(role_sid=role_sid)
    if len(role) != 1:
        raise Exception( 'Role with sid %s is not found'%role_sid )

    role = BasUserRoles.objects.filter(user=user_id, role=role[0].id)

    if role:
        return True
    return False



def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """

    request.session[SESSION_KEY] = user.id

    #if hasattr(request, 'user'):
    #    request.user = user

def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    request.session.flush()
    #if hasattr(request, 'user'):
    #    from django.contrib.auth.models import AnonymousUser
    #    request.user = AnonymousUser()

def is_authenticated(request):
    return request.session.get(SESSION_KEY, False)

def get_current_user(request):
    user_id = request.session.get(SESSION_KEY,None)

    if not user_id:
        return AnonymousUser()

    user = BasUser.objects.get(id=user_id)

    return user


def auth_user(request):
    error = None
    form = None
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            passwd = form.cleaned_data['passwd']

            user = authenticate(username=username, password=passwd)
            if user is not None:
                login(request, user)

                return HttpResponseRedirect("/")
            else:
                error = "Username/password is invalid!"

    if form == None:
        form = AuthForm()
    return render_to_response('auth.html', {'form':form, 'error':error})
