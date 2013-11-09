from __future__ import unicode_literals
from django import forms

from user_info.models import UserInfo
from guardian.models import Group
from real_group.models import RealGroup

from common.forms import SearchRealGroup
from common.forms import SearchProject
from common.forms import SearchUserInfo


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


class RTPForm(SearchProject):

    def clean(self):
        if 'RTP_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')
        
        return super(RTPForm, self).clean()


class RTUForm(SearchUserInfo):

    def clean(self):
        if 'RTU_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')

        return super(RTUForm, self).clean()


class UTRForm(SearchRealGroup):

    def clean(self):
        if 'UTR_submit' not in self.data:
            raise forms.ValidationError('Not Being Submitted')

        return super(UTRForm, self).clean()
