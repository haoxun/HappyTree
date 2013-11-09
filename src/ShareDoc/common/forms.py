from __future__ import unicode_literals
from django import forms

from project.models import Project
from real_group.models import RealGroup
from user_info.models import UserInfo

class BasicSearch(forms.Form):
    name = forms.CharField(required=True,
                           max_length=50)
    
    TargetModel = None

    def clean(self):
        name = self.cleaned_data.get('name', None)
        if name is not None:
            self._target_set = getattr(self, 'TargetModel').objects.filter(name__icontains=name)
        return self.cleaned_data

    def _get_target_set(self):
        if hasattr(self, '_target_set'):
            return getattr(self, '_target_set')
        else:
            return "None"


class SearchRealGroup(BasicSearch):
    TargetModel = RealGroup

    def _get_real_group_set(self):
        return super(SearchRealGroup, self)._get_target_set()
    real_group_set = property(_get_real_group_set)


class SearchProject(BasicSearch):
    TargetModel = Project

    def _get_project_set(self):
        return super(SearchProject, self)._get_target_set()
    project_set = property(_get_project_set)


class SearchUserInfo(BasicSearch):
    TargetModel = UserInfo

    def _get_user_info_set(self):
        return super(SearchUserInfo, self)._get_target_set()
    user_info_ser = property(_get_user_info_set)
