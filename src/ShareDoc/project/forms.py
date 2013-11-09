from __future__ import unicode_literals
from django import forms

from project.models import Project
from real_group.models import RealGroup
from user_info.models import UserInfo

from common.forms import SearchRealGroup
from common.forms import SearchProject
from common.forms import SearchUserInfo


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


class PTRForm(SearchRealGroup):

    def clean(self):
        if 'PTR_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        
        return super(PTRForm, self).clean()


class PTUForm(SearchUserInfo):

    def clean(self):
        if 'PTU_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')

        return super(PTUForm, self).clean()


class UTPForm(SearchProject):

    def clean(self):
        if 'UTP_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')

        return super(UTPForm, self).clean()
