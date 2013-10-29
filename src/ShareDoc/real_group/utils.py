from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
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
import json
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
        real_group_user_ac = UserInfo_RealGroup_AC.objects.create(
                        user_info=user_info,
                        real_group=real_group,
                        action_code=getattr(UserInfo_RealGroup_AC, direction),
                        action_status=UserInfo_RealGroup_AC.STATUS_WAIT)
        if direction == 'ACTION_RTU':
            assign_perm('real_group.process_user_real_group_ac',
                    user_info.user,
                    real_group_user_ac)
        else:
            real_group_user_set = get_users_with_perms(real_group)
            for user in real_group_user_set:
                if user.has_perm('real_group_management', real_group):
                    assign_perm('real_group.process_user_real_group_ac',
                                user,
                                real_group_user_ac)

class ApplyConfirmHandler(object):
    """
    handler of the situations that somebody search sth via a form.
    """
    def _apply_confirm_handler(self, 
                               request, 
                               applier, 
                               form_cls,
                               target_set_generator):
        form = form_cls(request.POST)
        if form.is_valid():
            target_set = target_set_generator(form, applier)
            json_data = json.dumps({
                            'error': False,
                            'data': target_set,
                        })
            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form.errors)
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
            json_data = json.dumps({
                            'error': error_dict,
                        })
            return HttpResponse(json_data, content_type='application/json')

class BasicInfoHandler(object):
    # form process, base on AJAX POST.
    def _basic_info_handler(self, request, target, form_cls, field_name):
        form = form_cls(request.POST)
        if form.is_valid():
            field = form.cleaned_data[field_name]
            setattr(target, field_name, field)
            target.save()
            json_data = json.dumps({
                            'error': False,
                            'data' : {field_name: field},
                        })
            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form.errors)
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
            json_data = json.dumps({
                            'error': True,
                            'data': error_dict,
                        })
            return HttpResponse(json_data, content_type='application/json')
