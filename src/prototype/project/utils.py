from __future__ import unicode_literals
import urllib
from django.http import Http404

def judge_in_manage_group_func(group_manager, request):
    for group in group_manager.all():
        if group.user_set.filter(username=request.user.username):
            return True
    return False

def judge_in_project_func(project, request):
    if project.manage_group.user_set.filter(username=request.user.username):
        return True
    for group in project.normal_group.all():
        if group.user_set.filter(username=request.user.username):
            return True
    return False
         
        


