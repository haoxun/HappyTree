
import urllib
from django.http import Http404

def url_with_querystring(path, **kwargs):
    return path + '?' + urllib.urlencode(kwargs)

def check_user_in_group_manager(user, group_info, flag):
    p = bool(group_info.manager_user.filter(username=user.username))
    q = bool(flag)
    if (not p and q) or (not q and p):
        raise Http404

def extract_from_GET(GET):
    group_info_id = GET.get('group_info_id', None)
    user_info_id = GET.get('user_info_id', None)
    if not all([group_info_id, user_info_id]):
        raise Http404
    group_info_id = int(group_info_id)
    user_info_id = int(user_info_id)
    return group_info_id, user_info_id
