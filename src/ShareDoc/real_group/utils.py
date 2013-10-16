from __future__ import unicode_literals
# django dependency
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from guardian.shortcuts import assign_perm, get_users_with_perms
# model 
from user_info.models import UserInfo
from real_group.models import RealGroup, UserInfo_RealGroup_AC
# form
# decorator
# util
# python library

def construct_user_real_group_ac(user_info_id, real_group_id, direction):
    if direction != 'ACTION_RTU' and direction != 'ACTION_UTR':
        raise PermissionDenied
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    if not UserInfo_RealGroup_AC.objects.filter(
            user_info=user_info,
            real_group=real_group,
            action_code=getattr(UserInfo_RealGroup_AC, direction),
            action_status=UserInfo_RealGroup_AC.STATUS_WAIT):
        # ensure there's only one ac
        real_group_to_user_ac = UserInfo_RealGroup_AC.objects.create(
                        user_info=user_info,
                        real_group=real_group,
                        action_code=getattr(UserInfo_RealGroup_AC, direction),
                        action_status=UserInfo_RealGroup_AC.STATUS_WAIT)
        if direction == 'ACTION_RTU':
            assign_perm('real_group.process_user_real_group_ac',
                    user_info.user,
                    real_group_to_user_ac)
        else:
            real_group_user_set = get_users_with_perms(real_group)
            for user in real_group_user_set:
                if user.has_perm('real_group_management', real_group):
                    assign_perm('real_group.process_user_real_group_ac',
                                user,
                                real_group_to_user_ac)



