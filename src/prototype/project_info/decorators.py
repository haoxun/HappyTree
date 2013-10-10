from functools import wraps
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from project_info.models import ProjectInfo
from group_info.models import GroupInfo

from django.http import Http404

def require_user_in_project_group(group_type, flag):
    if group_type not in ['normal_group', 'super_group']:
        raise TypeError("wrong group type!")
    def _wrap(func):
        @wraps(func)
        def _wrap_view(request, *args, **kwargs):
            project_info_id = int(kwargs.get('project_info_id'))
            project_info = ProjectInfo.objects.get(id=project_info_id)
            user_in = not flag
            # if user in group, then user must in normal group
            for group_info in getattr(project_info, group_type).all():
                if group_info.group.user_set.filter(username=request.user.username):
                    user_in = flag
                    break
            if not user_in:
                raise Http404
            return func(request, *args, **kwargs)
        return _wrap_view
    return _wrap

        
