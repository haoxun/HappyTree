from __future__ import unicode_literals

import hashlib

def gen_MD5_of_UploadedFile(file):
    m = hashlib.md5()
    while True:
        data = file.read()
        if not data:
            return m.hexdigest()
        m.update(data)

def message_judge_func(message, request):
    return message.creator == request.user

def judge_downloadable(file_info, project_info, user):
    require_perm = [file_info.READ, file_info.READ_AND_WRITE]
    # super group perm
    for group_info in project_info.super_group.all():
        if group_info.group.user_set.filter(username=user.username):
        # user in super group, return all perm
            return True
    # owner perm
    if file_info.owner == user:
        # user's owner, return file's owner_perm
        if file_info.owner_perm in require_perm:
            return True
        return False
    # group perm
    has_intersection = False
    for group_info in project_info.normal_group.all():
        user_set = group_info.group.user_set
        if user_set.filter(username=file_info.owner.username) \
                and user_set.filter(username=user.username):
            # file's owner and user in the same group
            group_perm = file_info.group_perm
            if group_perm in require_perm:
                return True
            # mark intersection
            has_intersection = True
    if has_intersection:
        return False
    # everyone's perm
    if file_info.everyone_perm in require_perm:
        return True
    return False

