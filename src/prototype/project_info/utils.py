import urllib
from django.http import Http404

def judge_func(group_info_manager, request):
    for group_info in group_info_manager.all():
        if group_info.group.user_set.filter(username=request.user.username):
            return True
    return False
        


