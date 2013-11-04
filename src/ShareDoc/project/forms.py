from __future__ import unicode_literals
from django import forms
from real_group.forms import GroupNameHandlerForm
from real_group.forms import AddUserForm
from project.models import Project
from real_group.models import RealGroup
from guardian.models import User


class ProjectNameHandlerForm(forms.Form):
    name = forms.CharField(required=True,
                           max_length=50,
                           min_length=3)

    def clean(self):
        if 'project_name_submit' not in self.data \
                and 'create_project_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data


class ProjectDescriptionHandlerForm(forms.Form):
    description = forms.CharField(required=False,
                                  max_length=500,
                                  widget=forms.Textarea)
    

    def clean(self):
        if 'project_description_submit' not in self.data \
                and 'create_project_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data


class AddRealGroupForm(GroupNameHandlerForm):
    def _get_add_real_group_set(self):
        if hasattr(self, '_add_real_group_set'):
            return self._add_real_group_set
        else:
            return "None"

    add_real_group_set = property(_get_add_real_group_set)

    def clean(self):
        if 'PTR_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        name = self.cleaned_data.get('name', None)
        if name is None:
            return self.cleaned_data
        self._add_real_group_set = RealGroup.objects.filter(name__icontains=name)
        return self.cleaned_data


class AddUserForm(AddUserForm):
    def clean(self):
        if 'PTU_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        if 'username' not in self.cleaned_data:
            return self.cleaned_data
        username = self.cleaned_data['username']
        self._add_user_set = User.objects.filter(username__icontains=username)
        return self.cleaned_data


class ApplyToProjectForm(ProjectNameHandlerForm):
    def _get_add_project_set(self):
        if hasattr(self, '_add_project_set'):
            return self._add_project_set
        else:
            return "None"

    add_project_set = property(_get_add_project_set)

    def clean(self):
        if 'UTP_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        if 'name' not in self.cleaned_data:
            return self.cleaned_data
        name = self.cleaned_data['name']
        self._add_project_set = Project.objects.filter(name__icontains=name)
        return self.cleaned_data


class RealGroupApplyToProjectForm(ApplyToProjectForm):
    def clean(self):
        if 'RTP_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        if 'name' not in self.cleaned_data:
            return self.cleaned_data
        name = self.cleaned_data['name']
        self._add_project_set = Project.objects.filter(name__icontains=name)
        return self.cleaned_data
