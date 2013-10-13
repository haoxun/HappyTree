from __future__ import unicode_literals

from django import forms
from project.models import Project
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
        if Project.objects.filter(name=project_name):
            # duplicate
            raise forms.ValidationError(
                    message=self.error_message['duplicate'].format(project_name))
        else:
            return self.cleaned_data

class ProjectDescriptionHandlerForm(forms.Form):
    project_description = forms.CharField(required=False,
                                          max_length=500)
    def clean(self):
        if 'project_description_submit' not in self.data \
                and 'create_project_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        return self.cleaned_data



class AddGroupForm(forms.Form):
    error_message = {
            'empty': 'Not exist group named {}',
    }

    group_name = forms.CharField(required=True)
    
    def clean(self):
        if 'add_group_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        group_name = self.cleaned_data.get('group_name', None)
        # validate group
        try:
            Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise forms.ValidationError(
                    message=self.error_message['empty'].format(username))
        else:
            return self.cleaned_data



