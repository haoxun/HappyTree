from __future__ import unicode_literals
# django dependency
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403, permission_required
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms, \
                               get_objects_for_user
# model 
from guardian.models import User, Group
from user_info.models import UserInfo
from real_group.models import RealGroup, UserInfo_RealGroup_AC
from project.models import UserInfo_Project_AC, RealGroup_Project_AC
# form
# decorator
# util
from user_info.utils import gen_models_debug_info
# python library
import operator

@login_required
def home_page(request):
    return render(request,
                  'user_info/home.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login_page')

@login_required
def accept_confirm_page(request):
    user_to_project_ac = []
    project_to_user_ac = []
    user_to_real_group_ac = []
    real_group_to_user_ac = []
    real_group_to_project_ac = []
    project_to_real_group_ac = []
    
    user_project_ac = \
            get_objects_for_user(request.user,
                                 'project.process_user_project_ac')
    real_group_project_ac = \
            get_objects_for_user(request.user, 
                                 'project.process_real_group_project_ac')
    user_real_group_ac = \
            get_objects_for_user(request.user,
                                 'real_group.process_user_real_group_ac')
    # classify
    real_group_set = get_objects_for_user(request.user, 
                                          'real_group.real_group_management')
    project_set = get_objects_for_user(request.user, 
                                       'project.project_management')

    for ac in user_project_ac:
        if ac.project in project_set:
            user_to_project_ac.append(ac)
        else:
            project_to_user_ac.append(ac)
    for ac in real_group_project_ac:
        if ac.project in project_set:
            real_group_to_project_ac.append(ac)
        elif ac.real_group in real_group_set:
            project_to_real_group_ac.append(ac)
    for ac in user_real_group_ac:
        if ac.real_group in real_group_set:
            user_to_real_group_ac.append(ac)
        else:
            real_group_to_user_ac.append(ac)

    # ordering
    def sort_ac(ac):
        return sorted(ac, key=lambda x: x.created_time, reverse=True)
    user_to_project_ac = sort_ac(user_to_project_ac)
    user_to_real_group_ac = sort_ac(user_to_real_group_ac)
    project_to_user_ac = sort_ac(project_to_user_ac)
    project_to_real_group_ac = sort_ac(project_to_real_group_ac)
    real_group_to_user_ac = sort_ac(real_group_to_user_ac)
    real_group_to_project_ac = sort_ac(real_group_to_project_ac)

    render_data_dict = {
            'user_to_project_ac': user_to_project_ac,
            'user_to_real_group_ac': user_to_real_group_ac,
            'project_to_user_ac': project_to_user_ac,
            'project_to_real_group_ac': project_to_real_group_ac,
            'real_group_to_user_ac': real_group_to_user_ac,
            'real_group_to_project_ac': real_group_to_project_ac,
    }

    return render(request,
                  'user_info/ac_list.html',
                  render_data_dict)
    

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
        
            
     
    

