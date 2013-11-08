from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
# auth dependency
from guardian.decorators import permission_required_or_403
from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
from guardian.shortcuts import get_objects_for_user
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup
# form
from real_group.forms import GroupNameHandlerForm
from real_group.forms import GroupDescriptionHandlerForm
from real_group.forms import AddUserForm
from real_group.forms import ApplyToGroupForm
from project.forms import RealGroupApplyToProjectForm
# decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# util
from django.template.loader import render_to_string
from ShareDoc.utils import url_with_querystring
from ShareDoc.utils import extract_from_GET
from real_group.utils import construct_user_real_group_ac
from real_group.utils import ApplyConfirmHandler
from real_group.utils import BasicInfoHandler
# python library
from datetime import datetime
import json


class GroupPage(View):
    """
    This class manage the present logic of group page.
    """
    @method_decorator(
        permission_required_or_403('real_group_membership',
                                   (RealGroup, 'id', 'real_group_id',)),
    )
    def dispatch(self, *args, **kwargs):
        return super(GroupPage, self).dispatch(*args, **kwargs)

    def get(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))

        render_data_dict = {
            'request': request,
            'real_group': real_group,
        }
        return render(request,
                      'real_group/group_page.html',
                      render_data_dict)

    def _get_html_response(self, request, real_group, template_name):
        render_data_dict = {
            'request': request,
            'real_group': real_group,
            'user_set': get_users_with_perms(real_group),
            'display_control': True,
        }
        html = render_to_string(template_name,
                                render_data_dict)
        return HttpResponse(html)

    def _handler_factory(self, request):
        if 'load_manager_list' in request.POST:
            return self._group_manager_list_handler
        elif 'load_member_list' in request.POST:
            return self._group_member_list_handler

    def _group_manager_list_handler(self, request, real_group):
        return self._get_html_response(request,
                                       real_group,
                                       'real_group/manager_list.html')

    def _group_member_list_handler(self, request, real_group):
        return self._get_html_response(request,
                                       real_group,
                                       'real_group/member_list.html')

    def post(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        handler = self._handler_factory(request)
        return handler(request, real_group)


class GroupListPage(View, ApplyConfirmHandler):
    """
    This class manage the process logic of presenting groups, including
    1. links to groups.
    2. searching groups to attend.
    3. create group.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupListPage, self).dispatch(*args, **kwargs)

    def get(self, request):
        form_apply_to_group = ApplyToGroupForm()
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        real_group_set = get_objects_for_user(
            request.user,
            'real_group.real_group_membership',
        )
        render_data_dict = {
            'form_apply_to_group': form_apply_to_group,
            'form_group_name': form_group_name,
            'form_group_description': form_group_description,
            'request': request,
            'real_group_set': real_group_set,
        }
        return render(request,
                      'real_group/group_list_page.html',
                      render_data_dict)

    def _handler_factory(self, request):
        if 'UTR_submit' in request.POST:
            return self._user_apply_to_real_group
        elif 'create_group_submit' in request.POST:
            return self._create_group

    def _add_group_generator(self, form, user_info):
        add_group_set = {}
        for real_group in form.add_group_set:
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
        return self._apply_confirm_handler(request,
                                           request.user.userinfo,
                                           ApplyToGroupForm,
                                           self._add_group_generator)

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

    def post(self, request):
        handler = self._handler_factory(request)
        return handler(request)


class GroupManagementPage(View, ApplyConfirmHandler, BasicInfoHandler):
    """
    This class manage the process logic of group management page.
    """
    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('real_group_management',
                      (RealGroup, 'id', 'real_group_id',)))
    def dispatch(self, *args, **kwargs):
        return super(GroupManagementPage, self).dispatch(*args, **kwargs)

    def get(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        # form
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = AddUserForm()
        form_apply_to_project = RealGroupApplyToProjectForm()
        render_data_dict = {
            'form_group_name': form_group_name,
            'form_group_description': form_group_description,
            'form_apply_to_project': form_apply_to_project,
            'form_add_user': form_add_user,
            'real_group': real_group,
        }
        return render(request,
                      'real_group/group_management_page.html',
                      render_data_dict)

    def _add_user_generator(self, form_add_user, real_group):
        add_user_set = {}
        for user in form_add_user.add_user_set:
            if user.has_perm('real_group_membership', real_group):
                # already in group, not display
                continue
            keywords = {'real_group_id': real_group.id,
                        'user_info_id': user.userinfo.id}
            add_user_set[user.username] = reverse(
                'invite_user_to_real_group',
                kwargs=keywords
            )
        return add_user_set

    def _add_project_set(self, form_apply_to_project, real_group):
        add_project_set = {}
        for project in form_apply_to_project.add_project_set:
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

    def _handler_factory(self, request):
        if "group_name_submit" in request.POST:
            return self._group_name_handler
        elif "group_description_submit" in request.POST:
            return self._group_description_handler
        elif "RTU_submit" in request.POST:
            return self._real_group_apply_to_user_handler
        elif "RTP_submit" in request.POST:
            return self._real_group_apply_to_project_handler
        elif "load_manager_list" in request.POST:
            return self._group_manager_list_handler
        elif "load_member_list" in request.POST:
            return self._group_member_list_handler
        else:
            raise PermissionDenied

    def _get_html_response(self, request, real_group, template_name):
        render_data_dict = {
            'request': request,
            'real_group': real_group,
            'user_set': get_users_with_perms(real_group),
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

    def _group_name_handler(self, request, real_group):
        return self._basic_info_handler(request,
                                        real_group,
                                        GroupNameHandlerForm,
                                        'name')

    def _group_description_handler(self, request, real_group):
        return self._basic_info_handler(request,
                                        real_group,
                                        GroupDescriptionHandlerForm,
                                        'description')

    def _real_group_apply_to_user_handler(self, request, real_group):
        return self._apply_confirm_handler(request,
                                           real_group,
                                           AddUserForm,
                                           self._add_user_generator)

    def _real_group_apply_to_project_handler(self, request, real_group):
        return self._apply_confirm_handler(request,
                                           real_group,
                                           RealGroupApplyToProjectForm,
                                           self._add_project_set)

    def post(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        handler = self._handler_factory(request)
        return handler(request, real_group)


@permission_required_or_403('real_group_management',
                            (RealGroup, 'id', 'real_group_id',))
def invite_user_to_real_group(request, user_info_id, real_group_id):
    construct_user_real_group_ac(user_info_id, real_group_id, "ACTION_RTU")
    return HttpResponse('OK')


@login_required
def user_apply_to_real_group(request, user_info_id, real_group_id):
    construct_user_real_group_ac(user_info_id, real_group_id, "ACTION_UTR")
    return HttpResponse('OK')


@permission_required_or_403('real_group_management',
                            (RealGroup, 'id', 'real_group_id',))
def delete_user_from_group(request, real_group_id, user_info_id):
    real_group_id = int(real_group_id)
    user_info_id = int(user_info_id)
    # authentication
    user = get_object_or_404(UserInfo, id=user_info_id).user
    real_group = get_object_or_404(RealGroup, id=real_group_id)
    # manager can not be remove from group
    if user.has_perm('real_group_ownership', real_group) \
            or user.has_perm('real_group_management', real_group):
        raise PermissionDenied
    # delete user
    real_group.group.user_set.remove(user)
    remove_perm('real_group_membership', user, real_group)
    return HttpResponse('OK')


@permission_required_or_403('real_group_management',
                            (RealGroup, 'id', 'real_group_id',))
def process_user_permission(request, real_group_id, user_info_id, decision):
    if decision == "True":
        tack_action = assign_perm
    elif decision == "False":
        tack_action = remove_perm
    else:
        raise PermissionDenied
    user = get_object_or_404(UserInfo, id=int(user_info_id)).user
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    tack_action('real_group_management', user, real_group)
    return HttpResponse('OK')
