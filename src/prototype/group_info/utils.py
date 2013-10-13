from __future__ import unicode_literals
import urllib
from django.http import Http404
from prototype.utils import exclusive_with_flag_results_Http404

def get_user_in_manager_group_manager(user, group_info):
    return group_info.manager.filter(username=user.username)

def assert_user_in_group_manager(*args, **kwargs):
    exclusive_with_flag_results_Http404(
            True,
            get_user_in_manager_group_manager(*args, **kwargs)
    )

def assert_user_not_in_group_manager(*args, **kwargs):
    exclusive_with_flag_results_Http404(
            False,
            get_user_in_manager_group_manager(*args, **kwargs)
    )

def judge_func(manager, request):
    return manager.filter(username=request.user.username)
