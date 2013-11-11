from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
# model
from user_info.models import UserInfo
from real_group.models import RealGroup
from notification.models import UserInfo_RealGroup_AC
# form
# decorator
# util
from django.template.loader import render_to_string
import json
# python library

def delete_user_from_group(real_group_id, user_info_id):
    # authentication
    user = get_object_or_404(UserInfo, id=int(user_info_id)).user
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    # manager can not be remove from group
    if user.has_perm('real_group_ownership', real_group):
        raise PermissionDenied
    # delete user
    real_group.group.user_set.remove(user)
    remove_perm('real_group_management', user, real_group)
    remove_perm('real_group_membership', user, real_group)


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
            action_status=UserInfo_RealGroup_AC.STATUS_WAIT,
        )
        if direction == 'ACTION_RTU':
            assign_perm(
                'notification.process_user_real_group_ac',
                user_info.user,
                real_group_user_ac,
            )
        else:
            real_group_user_set = get_users_with_perms(real_group)
            for user in real_group_user_set:
                if user.has_perm('real_group_management', real_group):
                    assign_perm(
                        'notification.process_user_real_group_ac',
                        user,
                        real_group_user_ac
                    )


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
                'data': {field_name: field},
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


class GroupUserHandler(object):

    def _get_html_response(self, request, real_group, template_name):
        render_data_dict = {
            'request': request,
            'real_group': real_group,
            'user_set': get_users_with_perms(real_group),
            'display_control': getattr(self, '_display_control'),
        }
        html = render_to_string(template_name,
                                render_data_dict)
        return HttpResponse(html)

    def _group_manager_list_handler(self, request, real_group):
        return self._get_html_response(request,
                                       real_group,
                                       'real_group/manager_list.html')

    def _group_member_list_handler(self, request, real_group):
        return self._get_html_response(request,
                                       real_group,
                                       'real_group/member_list.html')
