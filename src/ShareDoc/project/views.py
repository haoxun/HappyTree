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
from project.models import Project
from project.models import ProjectGroup
from message.models import Message
# form
from project.forms import ProjectNameHandlerForm
from project.forms import ProjectDescriptionHandlerForm
from project.forms import PTUForm
from project.forms import PTRForm
from project.forms import UTPForm
# decorator
from django.utils.decorators import method_decorator
# util
from common.utils import POSTHandler
from project.utils import AJAX_ProjectMessagePageHandler
from project.utils import AJAX_ProjectListPageHandler
from project.utils import NOTAJAX_ProjectListPageHandler
from project.utils import AJAX_ProjectFileListPageHandler
from project.utils import AJAX_ProjectManagementPageHandler
from project.utils import construct_user_project_ac
from project.utils import construct_real_group_project_ac
# python library


project_permissions = []
for permission, description in Project._meta.permissions:
    project_permissions.append(permission)


class ProjectMessagePage(AJAX_ProjectMessagePageHandler, POSTHandler):
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
        return self._handler(request, project)


class ProjectListPage(AJAX_ProjectListPageHandler,
                      NOTAJAX_ProjectListPageHandler,
                      POSTHandler):
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
        form_apply_to_project = UTPForm()
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

    def post(self, request):
        return self._handler(request)


class ProjectFileListPage(AJAX_ProjectFileListPageHandler,
                          POSTHandler):
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
        return self._handler(request, project)


class ProjectManagementPage(AJAX_ProjectManagementPageHandler,
                            POSTHandler):
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
        form_add_user = PTUForm()
        form_add_real_group = PTRForm()

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
