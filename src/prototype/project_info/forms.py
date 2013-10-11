from __future__ import unicode_literals

from django import forms
from project_info.models import ProjectInfo
from django.contrib.auth.models import Group

class ProjectNameHandlerForm(forms.Form):
    error_message = {
            'duplicate': 'Already has a project named {}',      
    }
    
    project_name = forms.CharField(required=True, 
                                   max_length=50, 
                                   min_length=3)
    def clean(self):
        if 'project_name_submit' not in self.data \
                and 'create_project_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        project_name = self.cleaned_data.get('project_name', None)
        if ProjectInfo.objects.filter(name=project_name):
            # duplicate
            raise forms.ValidationError(
                    message=self.error_message['duplicate'].format(project_name))
        else:
            return self.cleaned_data

class ProjectDescriptionHandlerForm(forms.Form):
    project_description = forms.CharField(required=False,
                                          max_length=5000)
    def clean(self):
        if 'project_description_submit' not in self.data \
                and 'create_project_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data



class AddGroupForm(forms.Form):
    error_message = {
            'empty': 'Not exist group named {}',
            'forbid_pattern': 'Group name could not start with [system][normal_group] or [system][super_group]',
    }

    group_name = forms.CharField(required=True)
    
    def clean(self):
        if 'add_group_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        group_name = self.cleaned_data.get('group_name', None)
        if group_name.startswith('[system][normal_group]') \
                or group_name.startswith('[system][normal_group]'):
            raise forms.ValidationError(
                    message=self.error_message['forbid_pattern'])

        # validate group
        try:
            Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise forms.ValidationError(
                    message=self.error_message['empty'].format(username))
        else:
            return self.cleaned_data



