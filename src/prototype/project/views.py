from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_info.models import UserInfo
from project.models import Project
from group_info.models import GroupInfo

from .forms import ProjectNameHandlerForm, ProjectDescriptionHandlerForm, \
                   AddGroupForm
from prototype.decorators import require_user_in
from prototype.utils import extract_from_GET, url_with_querystring
from .utils import judge_in_project_func, judge_in_manage_group_func
from datetime import datetime

@login_required
def show_project_list(request):
    group_set = [group \
                    for group in request.user.groups.all() \
                        if not group.groupinfo.real_flag]

    display_project_act_as_normal_user = {}
    display_project_act_as_manager = {} 
    for group in group_set:
        # get projects
        try:
            project = group.manage_in_project
            display_project_act_as_manager[project.id] = project.name
        except:
            pass
        # temperary operation, cause it should be an one-to-many relation,
        # but now it is implemented as many-to-many relation.
        project = group.normal_in_project.all()
        project = project[0] if project else None
        if project:
            display_project_act_as_normal_user[project.id] = project.name
    # exclusive operation
    for project_id, name in display_project_act_as_manager.items():
        if project_id in display_project_act_as_normal_user:
            del display_project_act_as_normal_user[project_id]

    # rendering
    render_data_dict = {
            'display_project_act_as_manager': display_project_act_as_manager,
            'display_project_act_as_normal_user': display_project_act_as_normal_user 
    }
    return render(request,
                  'project/project_list_page.html',
                  render_data_dict) 

@login_required
@require_user_in(
        judge_in_project_func,
        'project_id', 
        (Project, True, (None,))
)
def show_project_page(request, project_id):
    project_id = int(project_id)
    project = get_object_or_404(Project, id=project_id)
    display_manage_group = {}
    display_normal_group = {group.groupinfo.name: group.groupinfo.id \
                            for group in project.normal_group.all()}
    # test manager
    manage_group = project.manage_group
    display_manage_group[manage_group.groupinfo.name] = manage_group.groupinfo.id
    is_manager = bool(manage_group.user_set.filter(
                                            username=request.user.username))

    # rendering
    render_data_dict = {
            'project_name': project.name,
            'project_description': project.description,
            'project_id': project_id,
            'project_manager_group': display_manage_group,
            'project_normal_group': display_normal_group,
            'is_manager': is_manager,
    }
    return render(request,
                  'project/project_page.html',
                  render_data_dict)
    

@login_required
def create_project(request):
    if request.method == 'POST':
        form_project_name = ProjectNameHandlerForm(request.POST)
        form_project_description = ProjectDescriptionHandlerForm(request.POST)
        if form_project_name.is_valid() and form_project_description.is_valid():
            # get project info
            project_name = form_project_name.cleaned_data['project_name']
            project_description = \
                    form_project_description.cleaned_data['project_description']
            
            # create manager group and default group
            # manager group is for project management.
            # default group is for adding user individually.
            # create groups
            unique_manage_group_name = \
                    "".join(('[project][manage_group]', 
                             request.user.username, 
                             unicode(datetime.now())))
            unique_default_group_name = \
                    "".join(('[project][default_group]', 
                             request.user.username, 
                             unicode(datetime.now())))
            manage_group = Group(name=unique_manage_group_name)
            default_group = Group(name=unique_default_group_name)
            manage_group.save()
            default_group.save()
            # add user to manage_group
            manage_group.user_set.add(request.user)
            
            # create relate group_infos
            # only for saving the info of group, not the manager
            manage_group_info = GroupInfo(name="manage_group",
                                          group=manage_group,
                                          owner=request.user,
                                          real_flag=False)
            default_group_info = GroupInfo(name="default_group",
                                           group=default_group,
                                           owner=request.user,
                                           real_flag=False)
            manage_group_info.save()
            default_group_info.save()


            # project must be created after all above staff were finished.
            project = Project(name=project_name,
                              description=project_description,
                              manage_group=manage_group,
                              owner=request.user)
            project.save()

            # add manage_group info to project info
            # notice that the default group is treated as a normal group.
            project.normal_group.add(default_group)
            return redirect('project_page',
                             project_id=project.id)
    else:
        form_project_name = ProjectNameHandlerForm()
        form_project_description = ProjectDescriptionHandlerForm()

    #rendering
    render_data_dict= {
        'form_project_name': form_project_name,
        'form_project_description': form_project_description,
    }
    return render(request,
                  'project/create_project_page.html',
                  render_data_dict)

@login_required
@require_user_in(
        judge_in_manage_group_func,
        'project_id', 
        (Project, True, ('manage_group',))
)
def show_project_management_page(request, project_id):
    project_id = int(project_id)
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form_project_name = ProjectNameHandlerForm(request.POST)
        form_project_description = ProjectDescriptionHandlerForm(request.POST)
        form_add_group = AddGroupForm(request.POST)
        
        if form_project_name.is_valid():
            project_name = form_project_name.cleaned_data['project_name']
            project.name = project_name
            project.save()
            return redirect('project_management_page',
                            project_id=project_id)
        #if form_project_description.is_valid() \
        #        and 'project_description' in request.POST:
        if form_project_description.is_valid():
            project_description = \
                    form_project_description.cleaned_data['project_description']
            project.description = project_description
            project.save()
            return redirect('project_management_page',
                            project_id=project_id)
        if form_add_group.is_valid():
            group_name = form_add_group.cleaned_data['group_name']
            group = get_object_or_404(Group, name=group_name)
            # add to attended group
            project.attended_group.add(group)
            # real group isolation
            unique_project_group_name = \
                    "".join('[project][attended_group]', 
                            request.user.username, 
                            datetime.now())
            project_group = Group(name=unique_project_group_name)
            project_group.save()
            for user in group.user_set.all():
                project_group.user_set.add(user)
            project.normal_group.add(project_group)
            # group info
            project_group_info = GroupInfo(name='[attended]'+group_name,
                                           group=project_group,
                                           real_flag=False)

            return redirect('project_management_page',
                            project_id=project_id)
        
    else:
        form_project_name = ProjectNameHandlerForm()
        form_project_description = ProjectDescriptionHandlerForm()
        form_add_group = AddGroupForm()
        
    # rendering
    display_project_normal_group = \
            {group.name: {
                           'group_info_id': group.groupinfo.id,
                           'remove_url': url_with_querystring(
                                           reverse('delete_group_from_project'),
                                           project_id=project_id,
                                           group_info_id=group.groupinfo.id)
                } \
                for group in project.normal_group.all() \
                    if group.real_flag}
    render_data_dict = {
            'form_project_name': form_project_name,
            'form_project_description': form_project_description,
            'form_add_group': form_add_group,
            'project_normal_group': display_project_normal_group,       
            'project_id': project_id,
    }
    return render(request,
                  'project/project_management_page.html',
                  render_data_dict)

@login_required
@require_user_in(
        judge_in_manage_group_func,
        'project_id', 
        (Project, True, ('manage_group',))
)
def delete_group_from_project(request):
    project_id, group_info_id = map(int, extract_from_GET(
                        request.GET,
                        'project_id', 'group_info_id'
                        ))
    project = get_object_or_404(Project, id=project_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    group = get_object_or_404(project.normal_group, name=group_info.group.name)
    project.normal_group.remove(group)
    return redirect('project_management_page',
                    project_id=project_id)

    

    

