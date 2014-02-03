# -*- coding: utf-8 -*-

from django import forms
from models import RPUser
import re
from django.utils.translation import ugettext as _

class AuthForm(forms.Form):
    username = forms.CharField(label=_(u"Логін"))
    passwd = forms.CharField(label=_(u"Пароль"),widget=forms.PasswordInput(render_value=False))

class RegisterForm(forms.Form):
    login = forms.CharField(label=_(u"Логін"))
    passwd = forms.CharField(label=_(u"Пароль"),widget=forms.PasswordInput(render_value=False))
    rpasswd = forms.CharField(label=_(u"Повтор паролю"),widget=forms.PasswordInput(render_value=False))
    name = forms.CharField(label=_(u"П.І.Б."))
    #birthday = forms.CharField(label=u"Birthday")
    email = forms.CharField(label=_(u"E-mail"))
    region = forms.CharField(label=_(u"Область"))
    city = forms.CharField(label=_(u"Населений пункт"))

    def clean_login(self):
        login = self.cleaned_data['login']

        users = RPUser.objects.filter(login=login)

        if users:
            raise forms.ValidationError(_(u"Користувач з логіном %(login)s вже існує в системі! Будь ласка, введіть інший логін")%{'login':login})

        return login

    def clean_passwd(self):
        passwd = self.cleaned_data['passwd']
        rpasswd = self.data['rpasswd']

        if passwd != rpasswd:
            raise forms.ValidationError(_(u"Введені паролі не співпадають!"))

        return passwd

    def clean_email(self):
        email = self.cleaned_data['email']

        comp = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
        matched = re.match(comp, email)
        if not matched:
            raise forms.ValidationError(_(u"Введений e-mail не коректний! Будь ласка, введіть e-mail адресу в правильному форматі"))

        users = RPUser.objects.filter(email=email.lower())

        if users:
            raise forms.ValidationError(_(u"З даної e-mail адреси вже зареєстрований користувач!"))

        return email.lower()


class RecordCreateForm(forms.Form):
    service = forms.CharField(label=_("Service"))
    start_time = forms.CharField(label=_("Start time"))
    stop_time = forms.CharField(label=_("End time"))
    comment = forms.CharField(label=_("Comment"), required=False)
