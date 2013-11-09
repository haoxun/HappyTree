from __future__ import unicode_literals
from django import forms


class LoginForm(forms.Form):
    email = forms.CharField(max_length=254,
                            required=True)

    password = forms.CharField(required=True,
                               max_length=32,
                               min_length=32)
