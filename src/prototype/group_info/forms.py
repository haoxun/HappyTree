from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import Group, User

class GroupNameHandlerForm(forms.Form):
    error_message = {
            'duplicate': 'Already has a group named {}',      
            'forbid_pattern': 'Group name could not start with [system][normal_group] or [system][super_group]',
    }
    
    group_name = forms.CharField(required=True, 
                                 max_length=50, 
                                 min_length=3)
    def clean(self):
        # following pattern is reservered for group structure of project.
        if 'group_name_submit' not in self.data \
                and 'create_group_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        group_name = self.cleaned_data.get('group_name', None)
        if group_name.startswith('[system][normal_group]') \
                or group_name.startswith('[system][normal_group]'):
            raise forms.ValidationError(
                    message=self.error_message['forbid_pattern'])
        try:
            Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return self.cleaned_data
        else:
            raise forms.ValidationError(
                    message=self.error_message['duplicate'].format(group_name))


class GroupDescriptionHandlerForm(forms.Form):
    group_description = forms.CharField(required=False,
                                        max_length=5000)

    def clean(self):
        if 'group_description_submit' not in self.data \
                and 'create_group_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data


class AddUserForm(forms.Form):
    error_message = {
            'empty': 'Not exist user named {}',
    }

    username = forms.CharField(required=True)
    
    def clean(self):
        username = self.cleaned_data.get('username', None)
        # see https://github.com/django/django/blob/master/django/forms/forms.py
        # for explanation.
        if username == None:
            return
        # validate user
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                    message=self.error_message['empty'].format(username))
        else:
            return self.cleaned_data

