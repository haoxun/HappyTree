from __future__ import unicode_literals
from django import forms
from guardian.models import User
from guardian.models import Group
from real_group.models import RealGroup


class GroupNameHandlerForm(forms.Form):
    name = forms.CharField(required=True,
                           max_length=50,
                           min_length=3)

    def clean(self):
        # following pattern is reservered for group structure of project.
        if 'group_name_submit' not in self.data \
                and 'create_group_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")

        return self.cleaned_data


class GroupDescriptionHandlerForm(forms.Form):
    description = forms.CharField(required=False,
                                  max_length=5000,
                                  widget=forms.Textarea)

    def clean(self):
        if 'group_description_submit' not in self.data \
                and 'create_group_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data


class AddUserForm(forms.Form):
    username = forms.CharField(required=True)

    def _get_add_user_set(self):
        if hasattr(self, '_add_user_set'):
            return self._add_user_set
        else:
            return "None"

    add_user_set = property(_get_add_user_set)

    def clean(self):
        if 'RTU_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        if 'username' not in self.cleaned_data:
            return self.cleaned_data
        username = self.cleaned_data['username']
        self._add_user_set = User.objects.filter(username__icontains=username,
                                                 id__gte=0)
        return self.cleaned_data


class ApplyToGroupForm(GroupNameHandlerForm):
    def _get_add_group_set(self):
        if hasattr(self, '_add_group_set'):
            return self._add_group_set
        else:
            return "None"
    add_group_set = property(_get_add_group_set)

    def clean(self):
        if 'UTR_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        # https://github.com/django/django/blob/master/django/forms/forms.py
        # see _clean_fields
        # https://github.com/django/django/blob/master/django/forms/fields.py
        # see clean
        # if a field valiate some rules,
        # that value would not be in the cleaned_data
        if 'name' not in self.cleaned_data:
            return self.cleaned_data
        name = self.cleaned_data['name']
        self._add_group_set = RealGroup.objects.filter(name__icontains=name)
        return self.cleaned_data
