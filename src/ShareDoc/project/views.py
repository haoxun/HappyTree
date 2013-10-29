from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
# auth dependency
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403, permission_required
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms, \
                               get_objects_for_user
# model 
from guardian.models import User, Group
from user_info.models import UserInfo
from real_group.models import RealGroup, UserInfo_RealGroup_AC
from project.models import UserInfo_Project_AC, RealGroup_Project_AC, \
                           Project, ProjectGroup, Message
# form
from project.forms import ProjectNameHandlerForm, ProjectDescriptionHandlerForm, \
                          AddUserForm, AddRealGroupForm, ApplyToProjectForm
# decorator
from django.utils.decorators import method_decorator
# util
from project.utils import construct_user_project_ac, \
                          construct_real_group_project_ac
from real_group.utils import ApplyConfirmHandler, \
                             BasicInfoHandler
# python library
from datetime import datetime

project_permissions = [permission \
        for permission, description in Project._meta.permissions]

@login_required
def create_project_page(request):
    if request.method == 'POST':
        form_project_name = ProjectNameHandlerForm(request.POST)
        form_project_description = ProjectDescriptionHandlerForm(request.POST)
        if form_project_name.is_valid() and form_project_description.is_valid():
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
                                delete=False)
            project = Project.objects.create(
                        name=name,
                        description=description,
                        project_group=project_group)
            # asociate with creator
            group.user_set.add(request.user)
            for perm in project_permissions:
                assign_perm(perm, request.user, project)
            # return redirect('')
            return redirect('project_message_page', project_id=project.id)
    else:
        form_project_name = ProjectNameHandlerForm()
        form_project_description = ProjectDescriptionHandlerForm()

    render_data_dict = {
            'form_project_name': form_project_name,
            'form_project_description': form_project_description
    }
    return render(request,
                  'project/create_project_page.html',
                  render_data_dict)

@login_required
def project_list_page(request):
    project_set = get_objects_for_user(request.user, 'project.project_membership')

    if request.method == 'POST':
        form_apply_to_project = ApplyToProjectForm(request.POST)
    else:
        form_apply_to_project = ApplyToProjectForm()

    render_data_dict = {
            'project_set': project_set,
            'form_apply_to_project': form_apply_to_project,
    }
    return render(request,
                  'project/project_list_page.html',
                  render_data_dict)

@permission_required_or_403('project.project_membership', (Project, 'id', 'project_id'))
def project_file_list_page(request, project_id):
    project = get_object_or_404(Project, id=int(project_id))
    message_set = project.messages.filter(post_flag=True).order_by('-post_time')
    file_pointer_set = []
    for message in message_set:
        file_pointer_set.extend(message.file_pointers.all())

    render_data_dict = {
            'request': request,
            'project': project,
            'file_pointer_set': file_pointer_set,
    }
    return render(request,
                  'project/project_file_list_page.html',
                  render_data_dict)


class ProjectManagementPage(View, ApplyConfirmHandler, BasicInfoHandler):
    """
    This class handle the configuration process of project.
    """
    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('project.project_management', 
                      (Project, 'id', 'project_id',)))
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
            add_user_set[user.username] = \
                    reverse('invite_user_to_project',
                            kwargs=keywords)
        return add_user_set

    def _add_real_group_generator(self, form_add_real_group, project):
        add_real_group_set = {}
        for real_group in form_add_real_group.add_real_group_set:
            if project.real_groups.filter(id=real_group.id):
                # real group already in real_group
                continue
            keywords = {'project_id': project.id,
                        'real_group_id': real_group.id}
            add_real_group_set[real_group.name] = \
                    reverse('invite_real_group_to_project',
                            kwargs=keywords)
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

@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
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
    return redirect('project_management_page', project_id=project.id)


@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
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
    return redirect('project_management_page', project_id=project.id)


    
@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
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

    return redirect('project_management_page', project_id=project.id)

@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
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
    return redirect('project_management_page', project_id=project.id)


@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
def invite_user_to_project(request, project_id, user_info_id):
    construct_user_project_ac(user_info_id, project_id, 'ACTION_PTU')
    return redirect('project_management_page', project_id=project_id)
    


@permission_required_or_403('project.project_management', (Project, 'id', 'project_id'))
def invite_real_group_to_project(request, project_id, real_group_id):
    construct_real_group_project_ac(real_group_id, project_id, "ACTION_PTR")
    return redirect('project_management_page', project_id=project_id)

@login_required
def user_apply_to_project(request, user_info_id, project_id):
    construct_user_project_ac(user_info_id, project_id, "ACTION_UTP")
    return redirect('project_list_page')

@login_required
def real_group_apply_to_project(request, real_group_id, project_id):
    construct_real_group_project_ac(real_group_id, project_id, "ACTION_RTP")
    return HttpResponse('OK')
