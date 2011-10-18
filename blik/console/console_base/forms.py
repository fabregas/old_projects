# -*- coding: utf-8 -*-

from django import forms
from models import NmUser
import re
from django.utils.translation import ugettext as _

class AuthForm(forms.Form):
    username = forms.CharField(label=u"Login")
    passwd = forms.CharField(label=u"Password",widget=forms.PasswordInput(render_value=False))

