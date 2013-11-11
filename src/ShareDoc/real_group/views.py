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
from real_group.forms import RTUForm
from real_group.forms import RTPForm
from real_group.forms import UTRForm
# decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# util
from real_group.utils import construct_user_real_group_ac
from real_group.utils import delete_user_from_group
from real_group.utils import ApplyConfirmHandler
from real_group.utils import BasicInfoHandler
from real_group.utils import POSTHandler
from real_group.utils import AJAX_GroupPageHandler
from real_group.utils import AJAX_GroupListPageHandler
from real_group.utils import NOTAJAX_GroupListPageHandler
from real_group.utils import AJAX_GroupManagementPageHandler
# python library
from datetime import datetime
import json


class GroupPage(AJAX_GroupPageHandler, POSTHandler):
    """
    This class manage the present logic of group page.
    """
    def __init__(self, *args, **kwargs):
        super(GroupPage, self).__init__(*args, **kwargs)

    # for GroupUserHandler setting
    _display_control = True

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

    def post(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        return self._handler(request, real_group)


class GroupListPage(NOTAJAX_GroupListPageHandler,
                    AJAX_GroupListPageHandler,
                    POSTHandler):
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
        form_apply_to_group = UTRForm()
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

    def post(self, request):
        return self._handler(request)


class BasicGroupManagementPage(AJAX_GroupManagementPageHandler, 
                               POSTHandler):
    """
    This class manage the process logic of group management page.
    """

    def get(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        # form
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = RTUForm()
        form_apply_to_project = RTPForm()
        render_data_dict = {
            'form_group_name': form_group_name,
            'form_group_description': form_group_description,
            'form_apply_to_project': form_apply_to_project,
            'form_add_user': form_add_user,
            'real_group': real_group,
            'is_manager': not getattr(self, '_display_control'),
        }
        return render(request,
                      'real_group/group_management_page.html',
                      render_data_dict)

    def post(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        return self._handler(request, real_group)


class GroupManagementPageOfManager(BasicGroupManagementPage):
    # for GroupUserHandler setting
    _display_control = False

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('real_group_management',
                      (RealGroup, 'id', 'real_group_id',)))
    def dispatch(self, *args, **kwargs):
        return super(GroupManagementPageOfManager, self).dispatch(*args,
                                                                  **kwargs)


class GroupManagementPageOfMember(BasicGroupManagementPage):
    # for GroupUserHandler setting
    _display_control = True

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('real_group_membership',
                      (RealGroup, 'id', 'real_group_id',)))
    def dispatch(self, *args, **kwargs):
        return super(GroupManagementPageOfMember, self).dispatch(*args,
                                                                 **kwargs)


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
def manager_delete_user_from_group(request, real_group_id, user_info_id):
    delete_user_from_group(real_group_id, user_info_id)
    return redirect('group_list_page')

@permission_required_or_403('real_group_membership',
                            (RealGroup, 'id', 'real_group_id',))
def user_quit_from_group(request, real_group_id):
    delete_user_from_group(real_group_id, request.user.userinfo.id)
    return redirect('group_list_page')

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
