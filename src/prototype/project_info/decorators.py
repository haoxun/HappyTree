from functools import wraps
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from project_info.models import ProjectInfo
from group_info.models import GroupInfo

from django.http import Http404

def require_user_in_project(func):
    @wraps(func)
    def _wrap_view(request, *args, **kwargs):
        project_info_id = int(kwargs.get('project_info_id'))
        project_info = ProjectInfo.objects.get(id=project_info_id)
        user_in_project = False
        # if user in group, then user must in normal group
        for group_info in project_info.normal_group.all():
            if group_info.group.user_set.filter(username=request.user.username):
                user_in_project = True
                break
        if not user_in_project:
            raise Http404
        return func(request, *args, **kwargs)
    return _wrap_view

