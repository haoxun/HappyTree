from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.views.generic.base import View
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
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
from real_group.models import UserInfo_RealGroup_AC
from project.models import UserInfo_Project_AC 
from project.models import RealGroup_Project_AC
# form
# decorator
from django.utils.decorators import method_decorator
# util
from user_info.utils import gen_models_debug_info
from django.template.loader import render_to_string
# python library
import operator
import re


class HomePage(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomePage, self).dispatch(*args, **kwargs)

    def get(self, request):
        return render(request,
                      'user_info/home.html')
                      
    def post(self, request):
        project_set = get_objects_for_user(request.user,
                                           'project.project_membership')
        message_set = []
        for project in project_set:
            message_set.extend(project.messages.filter(post_flag=True))
        message_set = sorted(
            message_set,
            key=lambda x: x.post_time,
            reverse=True
        )

        return render(request,
                      'file_storage/message_list.html',
                      {'message_set': message_set})


class UserPage(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserPage, self).dispatch(*args, **kwargs)

    def get(self, request, user_info_id):
        user_info = get_object_or_404(UserInfo, id=int(user_info_id))
        return render(request,
                      'user_info/user_page.html',
                      {'user_info': user_info})

    def _handler_factory(self, request):
        if 'load_message_list' in request.POST:
            return self._message_list_handler

    def _message_list_handler(self, request, user_info):
        message_set = user_info.messages.filter(post_flag=True)
        message_set = sorted(
            message_set,
            key=lambda x: x.post_time,
            reverse=True
        )

        return render(request,
                      'file_storage/message_list.html',
                      {'message_set': message_set})

    def post(self, request, user_info_id):
        user_info = get_object_or_404(UserInfo, id=int(user_info_id))
        handler = self._handler_factory(request)
        return handler(request, user_info)


@login_required
def logout_user(request):
    logout(request)
    return redirect('login_page')


class ApplyConfirmPage(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApplyConfirmPage, self).dispatch(*args, **kwargs)

    def get(self, request):
        return render(request,
                      'user_info/ac_list.html')

    # response ac list
    def post(self, request):
        def sort_ac(ac):
            return sorted(ac, key=lambda x: x.created_time, reverse=True)

        def separate_user_project_ac(ac_list):
            UTP_ac = []
            PTU_ac = []
            for ac in ac_list:
                if ac.project in project_set:
                    UTP_ac.append(ac)
                else:
                    PTU_ac.append(ac)
            return sort_ac(UTP_ac), sort_ac(PTU_ac)

        def separate_real_group_project_ac(ac_list):
            RTP_ac = []
            PTR_ac = []
            for ac in ac_list:
                if ac.project in project_set:
                    RTP_ac.append(ac)
                elif ac.real_group in real_group_set:
                    PTR_ac.append(ac)
            return sort_ac(RTP_ac), sort_ac(PTR_ac)

        def separate_user_real_gorup_ac(ac_list):
            UTR_ac = []
            RTU_ac = []
            for ac in ac_list:
                if ac.real_group in real_group_set:
                    UTR_ac.append(ac)
                else:
                    RTU_ac.append(ac)
            return sort_ac(UTR_ac), sort_ac(RTU_ac)

        def check_empty(ac_template_mapping, html_ac):
            empty = True
            for ac, template_name, tag_name in ac_template_mapping:
                if len(ac) != 0:
                    empty = False
                    break
            if empty:
                return render_to_string('user_info/non_ac.html')
            else:
                return html_ac

        # non-direction relation
        user_project_ac = get_objects_for_user(
            request.user,
            'project.process_user_project_ac',
        )
        real_group_project_ac = get_objects_for_user(
            request.user,
            'project.process_real_group_project_ac',
        )
        user_real_group_ac = get_objects_for_user(
            request.user,
            'real_group.process_user_real_group_ac',
        )
        # Sth in which user can make decision
        real_group_set = get_objects_for_user(
            request.user,
            'real_group.real_group_management',
        )
        project_set = get_objects_for_user(
            request.user,
            'project.project_management',
        )

        UTP_ac, PTU_ac = separate_user_project_ac(user_project_ac)
        RTP_ac, PTR_ac = separate_real_group_project_ac(real_group_project_ac)
        UTR_ac, RTU_ac = separate_user_real_gorup_ac(user_real_group_ac)

        # rendering
        ac_template_mapping = [
            (UTP_ac, 'user_info/UTP.html', 'user_to_project_ac'),
            (PTU_ac, 'user_info/PTU.html', 'project_to_user_ac'),
            (RTP_ac, 'user_info/RTP.html', 'real_group_to_project_ac'),
            (PTR_ac, 'user_info/PTR.html', 'project_to_real_group_ac'),
            (UTR_ac, 'user_info/UTR.html', 'user_to_real_group_ac'),
            (RTU_ac, 'user_info/RTU.html', 'real_group_to_user_ac'),
        ]

        html_ac = []
        for ac, template_name, tag_name in ac_template_mapping:
            html_ac.append(
                render_to_string(template_name,
                                 {tag_name: ac}),
            )
        html_ac = check_empty(ac_template_mapping, html_ac)

        return HttpResponse("".join(html_ac))


@login_required
def process_user_project_ac(request, ac_id, decision):
    user_project_ac = get_object_or_404(UserInfo_Project_AC, id=int(ac_id))
    if user_project_ac.action_status != UserInfo_Project_AC.STATUS_WAIT:
        raise PermissionDenied
    user_info = user_project_ac.user_info
    project = user_project_ac.project
    project_group = project.project_group
    if decision == "ACCEPT":
        # add user
        project_group.group.user_set.add(user_info.user)
        assign_perm('project_membership', user_info.user, project)
        # add default permission
        if project_group.download:
            assign_perm('project_download', user_info.user, project)
        if project_group.upload:
            assign_perm('project_upload', user_info.user, project)
        if project_group.delete:
            assign_perm('project_delete', user_info.user, project)
        user_project_ac.action_status = UserInfo_Project_AC.STATUS_ACCEPT
    elif decision == "DENY":
        user_project_ac.action_status = UserInfo_Project_AC.STATUS_DENY
    else:
        raise PermissionDenied
    user_project_ac.save()
    for user in get_users_with_perms(project):
        remove_perm('project.process_user_project_ac',
                    user,
                    user_project_ac)
    return redirect('ac_page')


@login_required
def process_user_real_group_ac(request, ac_id, decision):
    user_real_group_ac = get_object_or_404(UserInfo_RealGroup_AC,
                                           id=int(ac_id))
    if user_real_group_ac.action_status != UserInfo_RealGroup_AC.STATUS_WAIT:
        raise PermissionDenied
    user_info = user_real_group_ac.user_info
    real_group = user_real_group_ac.real_group
    # add user to real_group
    if decision == "ACCEPT":
        real_group.group.user_set.add(user_info.user)
        assign_perm('real_group_membership',
                    user_info.user,
                    real_group)
        user_real_group_ac.action_status = UserInfo_RealGroup_AC.STATUS_ACCEPT
    elif decision == "DENY":
        user_real_group_ac.action_status = UserInfo_RealGroup_AC.STATUS_DENY
    else:
        raise PermissionDenied
    user_real_group_ac.save()
    # remove permissions
    for user in get_users_with_perms(real_group):
        remove_perm('real_group.process_user_real_group_ac',
                    user,
                    user_real_group_ac)
    return redirect('ac_page')


@login_required
def process_real_group_project_ac(request, ac_id, decision):
    real_group_project_ac = get_object_or_404(RealGroup_Project_AC,
                                              id=int(ac_id))
    if real_group_project_ac.action_status != RealGroup_Project_AC.STATUS_WAIT:
        raise PermissionDenied
    real_group = real_group_project_ac.real_group
    project = real_group_project_ac.project
    project_group = project.project_group
    if decision == "ACCEPT":
        for user in real_group.group.user_set.all():
            # add user to project
            project_group.group.user_set.add(user)
            assign_perm('project_membership',
                        user,
                        project)
            # set default permission
            if project_group.download:
                assign_perm('project_download', user, project)
            if project_group.upload:
                assign_perm('project_upload', user, project)
            if project_group.delete:
                assign_perm('project_delete', user, project)
        project.real_groups.add(real_group)
        real_group_project_ac.action_status = RealGroup_Project_AC.STATUS_ACCEPT
    elif decision == "DENY":
        real_group_project_ac.action_status = RealGroup_Project_AC.STATUS_DENY
    else:
        raise PermissionDenied
    real_group_project_ac.save()
    # remove permissions
    for user in get_users_with_perms(project):
        remove_perm('project.process_real_group_project_ac',
                    user,
                    real_group_project_ac)
    return redirect('ac_page')


# for test, showing all models
def models_page(request):
    from guardian.models import User, Group
    from user_info.models import UserInfo
    from real_group.models import RealGroup, UserInfo_RealGroup_AC
    from project.models import Project, Message, ProjectGroup
    from file_storage.models import FilePointer, UniqueFile
    from project.models import UserInfo_Project_AC, RealGroup_Project_AC
    model_set = [
        User,
        UserInfo,
        Group,
        RealGroup,
        Project,
        ProjectGroup,
        Message,
        FilePointer,
        UniqueFile,
        UserInfo_RealGroup_AC,
        UserInfo_Project_AC,
        RealGroup_Project_AC,
    ]
    printed_html = gen_models_debug_info(model_set)
    return render(request,
                  'test/test_page.html',
                  {'table': printed_html})
