
from django import forms

class AuthForm(forms.Form):
	username = forms.CharField(label=u"Username")
	passwd = forms.CharField(label=u"Password",widget=forms.PasswordInput(render_value=False))


