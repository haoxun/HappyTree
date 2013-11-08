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
from project.models import Project
from project.models import ProjectGroup
from project.models import Message
# form
from project.forms import ProjectNameHandlerForm
from project.forms import ProjectDescriptionHandlerForm
from project.forms import AddUserForm
from project.forms import AddRealGroupForm
from project.forms import ApplyToProjectForm
# decorator
from django.utils.decorators import method_decorator
# util
from django.template.loader import render_to_string
from project.utils import construct_user_project_ac
from project.utils import construct_real_group_project_ac
from real_group.utils import ApplyConfirmHandler
from real_group.utils import BasicInfoHandler
# python library
from datetime import datetime
import json


project_permissions = []
for permission, description in Project._meta.permissions:
    project_permissions.append(permission)


class ProjectMessagePage(View):
    @method_decorator(
        permission_required_or_403('project.project_membership',
                                   (Project, 'id', 'project_id')),
    )
    def dispatch(self, *args, **kwargs):
        return super(ProjectMessagePage, self).dispatch(*args, **kwargs)

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
        
        return render(request,
                      'project/project_message_page.html',
                      {'project': project})
    
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
        message_set = project.messages.filter(post_flag=True).order_by('-post_time')

        return render(request,
                      'message/message_list.html',
                      {'message_set': message_set})


class ProjectListPage(View, ApplyConfirmHandler):
    """
    This class handle the process of project list page, including
    1. presenting links to projects.
    2. search project to attend.
    3. create project.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectListPage, self).dispatch(*args, **kwargs)

    def get(self, request):
        project_set = get_objects_for_user(request.user,
                                           'project.project_membership')
        form_apply_to_project = ApplyToProjectForm()
        form_project_name = ProjectNameHandlerForm()
        form_project_description = ProjectDescriptionHandlerForm()

        render_data_dict = {
            'project_set': project_set,
            'form_apply_to_project': form_apply_to_project,
            'form_project_name': form_project_name,
            'form_project_description': form_project_description,
        }
        return render(request,
                      'project/project_list_page.html',
                      render_data_dict)

    def _add_project_generator(self, form_add_project, user_info):
        add_project_set = {}
        for project in form_add_project.add_project_set:
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

    def _handler_factory(self, request):
        if 'UTP_submit' in request.POST:
            return self._user_apply_to_project_handler
        if 'create_project_submit' in request.POST:
            return self._create_project

    def _user_apply_to_project_handler(self, request):
        return self._apply_confirm_handler(request,
                                           request.user.userinfo,
                                           ApplyToProjectForm,
                                           self._add_project_generator)

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
            for perm in project_permissions:
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

    def post(self, request):
        handler = self._handler_factory(request)
        return handler(request)


class ProjectFileListPage(View):
    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403('project.project_membership',
                                   (Project, 'id', 'project_id'))
    )
    def dispatch(self, *args, **kwargs):
        return super(ProjectFileListPage, self).dispatch(*args, **kwargs)

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
        render_data_dict = {
            'project': project,
        }
        return render(request,
                      'project/project_file_list_page.html',
                      render_data_dict)

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
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


class ProjectManagementPage(View, ApplyConfirmHandler, BasicInfoHandler):
    """
    This class handle the configuration process of project.
    """
    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403('project.project_management',
                                   (Project, 'id', 'project_id',))
    )
    def dispatch(self, *args, **kwargs):
        return super(ProjectManagementPage, self).dispatch(*args, **kwargs)

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
        form_project_name = ProjectNameHandlerForm()
        form_project_description = ProjectDescriptionHandlerForm()
        form_add_user = AddUserForm()
        form_add_real_group = AddRealGroupForm()

        render_data_dict = {
            'request': request,
            'project': project,
            'user_set': get_users_with_perms(project),
            'form_project_name': form_project_name,
            'form_project_description': form_project_description,
            'form_add_user': form_add_user,
            'form_add_real_group': form_add_real_group,
        }
        return render(request,
                      'project/project_management_page.html',
                      render_data_dict)

    def _add_user_generator(self, form_add_user, project):
        add_user_set = {}
        for user in form_add_user.add_user_set:
            if user.has_perm('project_management', project):
                # already in group, not display
                continue
            keywords = {'project_id': project.id,
                        'user_info_id': user.userinfo.id}
            add_user_set[user.username] = reverse(
                'invite_user_to_project',
                kwargs=keywords,
            )
        return add_user_set

    def _add_real_group_generator(self, form_add_real_group, project):
        add_real_group_set = {}
        for real_group in form_add_real_group.add_real_group_set:
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

    def _handler_factory(self, request):
        if 'project_name_submit' in request.POST:
            return self._project_name_handler
        elif 'project_description_submit' in request.POST:
            return self._project_description_handler
        elif 'PTR_submit' in request.POST:
            return self._project_apply_to_real_group_handler
        elif 'PTU_submit' in request.POST:
            return self._project_apply_to_user_handler
        elif 'load_manager_list' in request.POST:
            return self._manager_list_handler
        elif 'load_member_list' in request.POST:
            return self._member_list_handler
        elif 'load_default_perm' in request.POST:
            return self._default_perm_handler
    
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

    def _default_perm_handler(self, request, project):
        return self._get_html_response(request,
                                       project,
                                       'project/default_perm.html')

    def _project_name_handler(self, request, project):
        return self._basic_info_handler(request,
                                        project,
                                        ProjectNameHandlerForm,
                                        'name')

    def _project_description_handler(self, request, project):
        return self._basic_info_handler(request,
                                        project,
                                        ProjectDescriptionHandlerForm,
                                        'description')

    def _project_apply_to_user_handler(self, request, project):
        return self._apply_confirm_handler(request,
                                           project,
                                           AddUserForm,
                                           self._add_user_generator)

    def _project_apply_to_real_group_handler(self, request, project):
        return self._apply_confirm_handler(request,
                                           project,
                                           AddRealGroupForm,
                                           self._add_real_group_generator)

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=int(project_id))
        handler = self._handler_factory(request)
        return handler(request, project)

@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def apply_default_perm_to_all(request, project_id):
    project = get_object_or_404(Project, id=int(project_id))
    project_group = project.project_group
    for user in project_group.group.user_set.all():
        if user.has_perm('project_management', project):
            continue
        # remove
        remove_perm('project_download', user, project)
        remove_perm('project_upload', user, project)
        remove_perm('project_delete', user, project)
        # assign
        if project_group.download:
            assign_perm('project_download', user, project)
        if project_group.upload:
            assign_perm('project_upload', user, project)
        if project_group.delete:
            assign_perm('project_delete', user, project)

    return HttpResponse('OK')

@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def process_user_role_on_project(request, project_id, user_info_id, decision):
    project = get_object_or_404(Project, id=int(project_id))
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    # authentication
    # forbid if user not in project or user is the owner of project.
    if not user_info.user.has_perm('project_membership', project) \
            or user_info.user.has_perm('project_ownership', project):
        raise PermissionDenied
    # process
    if decision == "True":
        # set user as manager
        for perm in project_permissions:
            if perm == 'project_ownership':
                continue
            assign_perm(perm, user_info.user, project)
    elif decision == "False":
        # remove user's management permission
        remove_perm('project_management', user_info.user, project)
        if not project.project_group.download:
            remove_perm('project_download', user_info.user, project)
        if not project.project_group.upload:
            remove_perm('project_upload', user_info.user, project)
        if not project.project_group.delete:
            remove_perm('project_delete', user_info.user, project)
    else:
        raise PermissionDenied
    return HttpResponse('OK')


@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def delete_user_from_project(request, project_id, user_info_id):
    project = get_object_or_404(Project, id=int(project_id))
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    # authentication
    # forbid if user not in project or user is the manager of project.
    if not user_info.user.has_perm('project_membership', project) \
            or user_info.user.has_perm('project_management', project):
        raise PermissionDenied
    # delete user from project group
    project.project_group.group.user_set.remove(user_info.user)
    # remove perms
    for perm in project_permissions:
        remove_perm(perm, user_info.user, project)
    return HttpResponse('OK')


@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def process_user_permission_on_project(request,
                                       project_id,
                                       user_info_id,
                                       kind,
                                       decision):
    """
    This process the exception permission on user.
    kind should be in 'download', 'upload', 'delete',
    decision should either be "True" or "False",
    """
    project = get_object_or_404(Project, id=int(project_id))
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    # decide action
    if decision == "True":
        take_action = assign_perm
    elif decision == "False":
        take_action = remove_perm
    else:
        raise PermissionDenied
    # take action with respect to kind
    if kind not in ['download', 'upload', 'delete']:
        raise PermissionDenied
    perm = "project_{}".format(kind)
    take_action(perm, user_info.user, project)

    return HttpResponse('OK')


@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def process_default_permission_on_project(request,
                                          project_id,
                                          kind,
                                          decision):
    """
    This process the default
    kind should be in 'download', 'upload', 'delete',
    decision should either be "True" or "False",
    """
    project = get_object_or_404(Project, id=int(project_id))
    project_group = project.project_group
    # decide action
    if decision == "True":
        val = True
    elif decision == "False":
        val = False
    else:
        raise PermissionDenied
    # take action with respect to kind
    if kind not in ['download', 'upload', 'delete']:
        raise PermissionDenied
    setattr(project_group, kind, val)
    project_group.save()

    return HttpResponse('OK')


@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def invite_user_to_project(request, project_id, user_info_id):
    construct_user_project_ac(user_info_id, project_id, 'ACTION_PTU')
    return HttpResponse('OK')


@permission_required_or_403('project.project_management',
                            (Project, 'id', 'project_id'))
def invite_real_group_to_project(request, project_id, real_group_id):
    construct_real_group_project_ac(real_group_id, project_id, "ACTION_PTR")
    return HttpResponse('OK')


@login_required
def user_apply_to_project(request, user_info_id, project_id):
    construct_user_project_ac(user_info_id, project_id, "ACTION_UTP")
    return HttpResponse('OK')


@login_required
def real_group_apply_to_project(request, real_group_id, project_id):
    construct_real_group_project_ac(real_group_id, project_id, "ACTION_RTP")
    return HttpResponse('OK')
