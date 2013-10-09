from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from user_status.models import UserInfo
from project_info.models import ProjectInfo


@login_required
def show_project_list(request):
    group_set = request.user.groups.all()
    group_info_set = [group.groupinfo for group in group_set]
    
    display_project_act_as_normaluser = {}
    display_project_act_as_manager = {} 
    for group_info in group_info_set:
        for project in group_info.normal_in_project.all():
            display_project_act_as_normaluser[project.id] = project.name
        
        for project in group_info.super_in_project.all():
            display_project_act_as_manager[project.id] = project.name

    # rendering
    render_data_dict = {
            'display_project_act_as_manager': display_project_act_as_manager,
            'display_project_act_as_normaluser': display_project_act_as_normaluser
    }
    return render(request,
                  'project_info/project_list_page.html',
                  render_data_dict) 

@login_required
def show_project_page(request):
    pass


