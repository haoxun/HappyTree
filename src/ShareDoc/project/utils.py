from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.core.urlresolvers import reverse
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import get_users_with_perms
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup
from project.models import Project
from project.models import ProjectGroup
from message.models import Message
from notification.models import UserInfo_Project_AC
from notification.models import RealGroup_Project_AC
# form
from project.forms import ProjectNameHandlerForm
from project.forms import ProjectDescriptionHandlerForm
from project.forms import PTUForm
from project.forms import PTRForm
from project.forms import UTPForm
# decorator
# util
from common.utils import ApplyConfirmHandler
from common.utils import BasicInfoHandler
from django.template.loader import render_to_string
# python library
from datetime import datetime
import json


class AJAX_ProjectMessagePageHandler(object):

    def __init__(self, *args, **kwargs):
        super(AJAX_ProjectMessagePageHandler, self).__init__(*args, **kwargs)

        project_message_page_handler = [
            ('load_message_list', self._message_list_handler),
        ]

        self._register_handler(project_message_page_handler)
    
    def _message_list_handler(self, request, project):
        message_set = project.messages.filter(post_flag=True).order_by('-post_time')

        return render(request,
                      'message/message_list.html',
                      {'message_set': message_set})


class AJAX_ProjectListPageHandler(ApplyConfirmHandler):

    def __init__(self, *args, **kwargs):
        super(AJAX_ProjectListPageHandler, self).__init__(*args, **kwargs)

        project_list_page_handler = [
            ('UTP_submit', self._user_apply_to_project_handler),
        ]

        self._register_handler(project_list_page_handler)
        
    def _add_project_generator(self, form_add_project, user_info):
        add_project_set = {}
        for project in form_add_project.project_set:
            if user_info.user.has_perm('project_membership', project):
                # already in proejct, not display
                continue
            keywords = {'project_id': project.id,
                        'user_info_id': user_info.id}
            add_project_set[project.name] = reverse(
                'user_apply_to_project',
                kwargs=keywords,
            )
        return add_project_set

    def _user_apply_to_project_handler(self, request):
        return self._apply_confirm_handler(
            request,
            request.user.userinfo,
            UTPForm,
            self._add_project_generator
        )

class NOTAJAX_ProjectListPageHandler(ApplyConfirmHandler):

    def __init__(self, *args, **kwargs):
        super(NOTAJAX_ProjectListPageHandler, self).__init__(*args, **kwargs)

        project_list_page_handler = [
            ('create_project_submit', self._create_project),
        ]

        self._register_handler(project_list_page_handler)

    def _create_project(self, request):
        form_project_name = ProjectNameHandlerForm(request.POST)
        form_project_description = ProjectDescriptionHandlerForm(request.POST)
        if form_project_name.is_valid() \
                and form_project_description.is_valid():
            # extract data
            name = form_project_name.cleaned_data['name']
            description = form_project_description.cleaned_data['description']
            # create project
            unique_name = (
                '[project]',
                request.user.username,
                unicode(datetime.now()),
            )
            unique_name = "".join(unique_name)

            group = Group.objects.create(name=unique_name)
            project_group = ProjectGroup.objects.create(
                group=group,
                download=True,
                upload=False,
                delete=False,
            )
            project = Project.objects.create(
                name=name,
                description=description,
                project_group=project_group,
            )
            # asociate with creator
            group.user_set.add(request.user)
            for perm, description in Project._meta.permissions:
                assign_perm(perm, request.user, project)
             # response json data.
            keywords = {'project_id': project.id}
            json_data = json.dumps({
                'error': False,
                'url': reverse('project_message_page',
                               kwargs=keywords),
            })

            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form_project_name.errors)
            error_dict.update(form_project_description.errors)
            error_list = []
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
                error_list.append(key + ":" + error_dict[key])
            json_data = json.dumps({
                'error': "; ".join(error_list),
                'url': None,
            })

            return HttpResponse(json_data, content_type='application/json')


class AJAX_ProjectFileListPageHandler(object):

    def __init__(self, *args, **kwargs):
        super(AJAX_ProjectFileListPageHandler, self).__init__(*args, **kwargs)

        project_file_list_handler = [
            ('load_file_list', self._project_file_list_handler),
        ]

        self._register_handler(project_file_list_handler)

    def _project_file_list_handler(self, request, project):

        message_set = project.messages.filter(post_flag=True).order_by('-post_time')
        file_pointer_set = []
        for message in message_set:
            file_pointer_set.extend(message.file_pointers.all())
        render_data_dict = {
            'project': project,
            'file_pointer_set': file_pointer_set,
        }
        return render(request,
                      'project/project_file_list.html',
                      render_data_dict)

class ProjectUserHandler(object):

    def _get_html_response(self, request, project, template_name):
        render_data_dict = {
            'request': request,
            'project': project,
            'user_set': get_users_with_perms(project),
        }
        html = render_to_string(template_name,
                                render_data_dict)
        return HttpResponse(html)

    def _manager_list_handler(self, request, project):
        return self._get_html_response(request,
                                       project,
                                       'project/manager_list.html')

    def _member_list_handler(self, request, project):
        return self._get_html_response(request,
                                       project,
                                       'project/member_list.html')



class AJAX_ProjectManagementPageHandler(ProjectUserHandler,
                                        ApplyConfirmHandler,
                                        BasicInfoHandler):

    def __init__(self, *args, **kwargs):
        super(AJAX_ProjectManagementPageHandler, self).__init__(*args, **kwargs)

        project_management_page_handler = [
            ('load_manager_list', self._manager_list_handler),
            ('load_member_list', self._member_list_handler),
            ('load_default_perm', self._default_perm_handler),
            ('project_name_submit', self._project_name_handler),
            ('project_description_submit', self._project_description_handler),
            ('PTR_submit', self._project_apply_to_real_group_handler),
            ('PTU_submit', self._project_apply_to_user_handler),
        ]
        self._register_handler(project_management_page_handler)

    def _add_user_generator(self, form_add_user, project):
        add_user_info_set = {}
        for user_info in form_add_user.user_info_set:
            if user_info.user.has_perm('project_management', project):
                # already in group, not display
                continue
            keywords = {'project_id': project.id,
                        'user_info_id': user_info.id}
            add_user_info_set[user_info.name] = reverse(
                'invite_user_to_project',
                kwargs=keywords,
            )
        return add_user_info_set

    def _add_real_group_generator(self, form_add_real_group, project):
        add_real_group_set = {}
        for real_group in form_add_real_group.real_group_set:
            if project.real_groups.filter(id=real_group.id):
                # real group already in real_group
                continue
            keywords = {'project_id': project.id,
                        'real_group_id': real_group.id}
            add_real_group_set[real_group.name] = reverse(
                'invite_real_group_to_project',
                kwargs=keywords,
            )
        return add_real_group_set

    def _default_perm_handler(self, request, project):
        return self._get_html_response(
            request,
            project,
            'project/default_perm.html',
        )

    def _project_name_handler(self, request, project):
        return self._basic_info_handler(
            request,
            project,
            ProjectNameHandlerForm,
            'name',
        )

    def _project_description_handler(self, request, project):
        return self._basic_info_handler(
            request,
            project,
            ProjectDescriptionHandlerForm,
            'description',
        )

    def _project_apply_to_user_handler(self, request, project):
        return self._apply_confirm_handler(
            request,
            project,
            PTUForm,
            self._add_user_generator,
        )

    def _project_apply_to_real_group_handler(self, request, project):
        return self._apply_confirm_handler(
            request,
            project,
            PTRForm,
            self._add_real_group_generator,
        )


def construct_user_project_ac(user_info_id, project_id, direction):
    if direction != 'ACTION_PTU' and direction != 'ACTION_UTP':
        raise PermissionDenied
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    project = get_object_or_404(Project, id=int(project_id))
    if not UserInfo_Project_AC.objects.filter(
            user_info=user_info,
            project=project,
            action_code=getattr(UserInfo_Project_AC, direction),
            action_status=UserInfo_Project_AC.STATUS_WAIT):
        # ensure there's only one ac
        project_user_ac = UserInfo_Project_AC.objects.create(
            user_info=user_info,
            project=project,
            action_code=getattr(UserInfo_Project_AC, direction),
            action_status=UserInfo_Project_AC.STATUS_WAIT
        )
        if direction == 'ACTION_PTU':
            assign_perm(
                'notification.process_user_project_ac',
                user_info.user,
                project_user_ac,
            )
        else:
            project_user_set = get_users_with_perms(project)
            for user in project_user_set:
                if user.has_perm('project_management', project):
                    assign_perm(
                        'notification.process_user_project_ac',
                        user,
                        project_user_ac,
                    )


def construct_real_group_project_ac(real_group_id, project_id, direction):
    if direction != 'ACTION_PTR' and direction != 'ACTION_RTP':
        raise PermissionDenied
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    project = get_object_or_404(Project, id=int(project_id))
    if not RealGroup_Project_AC.objects.filter(
            real_group=real_group,
            project=project,
            action_code=getattr(RealGroup_Project_AC, direction),
            action_status=RealGroup_Project_AC.STATUS_WAIT):
        # ensure there's only one ac
        real_group_project_ac = RealGroup_Project_AC.objects.create(
            real_group=real_group,
            project=project,
            action_code=getattr(RealGroup_Project_AC, direction),
            action_status=RealGroup_Project_AC.STATUS_WAIT,
        )
        if direction == 'ACTION_PTR':
            real_group_user_set = get_users_with_perms(real_group)
            for user in real_group_user_set:
                if user.has_perm('real_group_management', real_group):
                    assign_perm(
                        'notification.process_real_group_project_ac',
                        user,
                        real_group_project_ac,
                    )
        elif direction == 'ACTION_RTP':
            project_user_set = get_users_with_perms(project)
            for user in project_user_set:
                if user.has_perm('project_management', project):
                    assign_perm(
                        'notification.process_real_group_project_ac',
                        user,
                        real_group_project_ac,
                    )
