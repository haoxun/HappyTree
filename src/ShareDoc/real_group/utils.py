from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic.base import View
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup
from notification.models import UserInfo_RealGroup_AC
# form
from real_group.forms import RTUForm
from real_group.forms import RTPForm
from real_group.forms import UTRForm
from real_group.forms import GroupNameHandlerForm
from real_group.forms import GroupDescriptionHandlerForm
# decorator
# util
from django.template.loader import render_to_string
# python library
from datetime import datetime
import json


class POSTHandler(View):
    """
    Abstration of handling AJAX HTTP POST 
    """
    def __init__(self, *args, **kwargs):
        super(POSTHandler, self).__init__(*args, **kwargs)
        self._registered_handler = []

    def _register_handler(self, handlers):
        self._registered_handler.extend(handlers)

    def _handler_factory(self, request):
        _registered_handler = getattr(self, '_registered_handler')
        for trigger, handler in _registered_handler:
            if trigger in request.POST:
                return handler
        return None
    
    def _handler(self, request, *args, **kwargs):
        handler = self._handler_factory(request)
        return handler(request, *args, **kwargs)


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

class AJAX_GroupPageHandler(GroupUserHandler):

    def __init__(self, *args, **kwargs):
        super(AJAX_GroupPageHandler, self).__init__(*args, **kwargs)

        group_page_handler = [
            ('load_manager_list', self._group_manager_list_handler),
            ('load_member_list', self._group_member_list_handler),
        ]
        self._register_handler(group_page_handler)



class AJAX_GroupListPageHandler(ApplyConfirmHandler):

    def __init__(self, *args, **kwargs):
        super(AJAX_GroupListPageHandler, self).__init__(*args, **kwargs)

        group_list_page_handler = [
            ('UTR_submit', self._user_apply_to_real_group),
        ]
        self._register_handler(group_list_page_handler)

    def _add_group_generator(self, form, user_info):
        add_group_set = {}
        for real_group in form.real_group_set:
            if user_info.user.has_perm('real_group_membership', real_group):
                # user already in group
                continue
            keywords = {'user_info_id': user_info.id,
                        'real_group_id': real_group.id}
            add_group_set[real_group.name] = reverse(
                'user_apply_to_real_group',
                kwargs=keywords,
            )
        return add_group_set

    def _user_apply_to_real_group(self, request):
        return self._apply_confirm_handler(
            request,
            request.user.userinfo,
            UTRForm,
            self._add_group_generator,
        )


class NOTAJAX_GroupListPageHandler(object):

    def __init__(self, *args, **kwargs):
        super(NOTAJAX_GroupListPageHandler, self).__init__(*args, **kwargs)

        group_list_page_handler = [
            ('create_group_submit', self._create_group),
        ]
        self._register_handler(group_list_page_handler)

    def _create_group(self, request):
        form_group_name = GroupNameHandlerForm(request.POST)
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        if form_group_name.is_valid() and form_group_description.is_valid():
            # create group
            name = form_group_name.cleaned_data['name']
            description = \
                    form_group_description.cleaned_data['description']
            # use user name + created time as group name
            unique_name = (
                '[real]',
                request.user.username,
                unicode(datetime.now()),
            )
            unique_name = "".join(unique_name)
            group = Group.objects.create(name=unique_name)
            # create related group info to handle group information
            real_group = RealGroup.objects.create(name=name,
                                                  description=description,
                                                  group=group)
            # set group's management permission to user
            assign_perm('real_group_ownership', request.user, real_group)
            assign_perm('real_group_management', request.user, real_group)
            assign_perm('real_group_membership', request.user, real_group)
            # relate user to group
            group.user_set.add(request.user)
            # response json data.
            keywords = {'real_group_id': real_group.id}
            json_data = json.dumps({
                'error': False,
                'url': reverse('group_page',
                               kwargs=keywords),
            })
            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form_group_name.errors)
            error_dict.update(form_group_description.errors)
            error_list = []
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
                error_list.append(key + ":" + error_dict[key])
            json_data = json.dumps({
                'error': "; ".join(error_list),
                'url': None,
            })
            return HttpResponse(json_data, content_type='application/json')


class AJAX_GroupManagementPageHandler(ApplyConfirmHandler,
                                      BasicInfoHandler,
                                      GroupUserHandler):

    def __init__(self, *args, **kwargs):
        super(AJAX_GroupManagementPageHandler, self).__init__(*args, **kwargs)

        group_management_page_handler = [
            ('group_name_submit', self._group_name_handler),
            ('group_description_submit', self._group_description_handler),
            ('RTU_submit', self._real_group_apply_to_user_handler),
            ('RTP_submit', self._real_group_apply_to_project_handler),
            ('load_manager_list', self._group_manager_list_handler),
            ('load_member_list', self._group_member_list_handler),
        ]
        self._register_handler(group_management_page_handler)

    def _add_user_generator(self, form_add_user, real_group):
        add_user_info_set = {}
        for user_info in form_add_user.user_info_set:
            if user_info.user.has_perm('real_group_membership', real_group):
                # already in group, not display
                continue
            keywords = {'real_group_id': real_group.id,
                        'user_info_id': user_info.id}
            add_user_info_set[user_info.name] = reverse(
                'invite_user_to_real_group',
                kwargs=keywords
            )
        return add_user_info_set

    def _add_project_set(self, form_apply_to_project, real_group):
        add_project_set = {}
        for project in form_apply_to_project.project_set:
            if project.real_groups.filter(id=real_group.id):
                # real group already in project
                continue
            keywords = {'real_group_id': real_group.id,
                        'project_id': project.id}
            add_project_set[project.name] = reverse(
                'real_group_apply_to_project',
                kwargs=keywords
            )
        return add_project_set

    def _group_name_handler(self, request, real_group):
        return self._basic_info_handler(
            request,
            real_group,
            GroupNameHandlerForm,
            'name',
        )

    def _group_description_handler(self, request, real_group):
        return self._basic_info_handler(
            request,
            real_group,
            GroupDescriptionHandlerForm,
            'description'
        )

    def _real_group_apply_to_user_handler(self, request, real_group):
        return self._apply_confirm_handler(
            request,
            real_group,
            RTUForm,
            self._add_user_generator
        )

    def _real_group_apply_to_project_handler(self, request, real_group):
        return self._apply_confirm_handler(
            request,
            real_group,
            RTPForm,
            self._add_project_set
        )
