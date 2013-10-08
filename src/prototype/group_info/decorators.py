from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from group_info.models import GroupInfo

def set_group_info_id_from_GET_to_kwargs(func):
    @wraps(func)
    def _warp_view(request, *args, **kwargs):
        if 'group_info_id' in request.GET:
            kwargs['group_info_id'] = request.GET['group_info_id']
        return func(request, *args, **kwargs)
    return _warp_view

def require_user_in_group(flag):
    def _wrap_flag(func):
        @wraps(func)
        def _wrap_view(request, *args, **kwargs):
            group_info_id = kwargs.get('group_info_id')
            group_info_id = int(group_info_id)
            group_info = get_object_or_404(GroupInfo, id=group_info_id)
            if not group_info.real_group:
                raise Http404
            # exclusive or
            p = bool(flag)
            q = bool(request.user.groups.filter(name=group_info.group.name))
            if (not p and q) or (not q and p):
                raise Http404
            return func(request, *args, **kwargs)
        return _wrap_view
    return _wrap_flag

def require_user_is_manager(flag):
    def _wrap_flag(func):
        @wraps(func)
        def _wrap_view(request, *args, **kwargs):
            group_info_id = kwargs.get('group_info_id')
            group_info_id = int(group_info_id)
            group_info = get_object_or_404(GroupInfo, id=group_info_id)
            # exclusive or
            p = bool(flag)
            q = bool(group_info.manager_user.filter(username=request.user.username))
            if (not p and q) or (not q and p):
                raise Http404
            return func(request, *args, **kwargs)
        return _wrap_view
    return _wrap_flag
    
