# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from group_info.models import GroupInfo
from .forms import CreateGroupForm

@login_required
def create_group(request):
    if request.method == "POST":
        form = CreateGroupForm(request.POST)    
        if form.is_valid():
            # create group
            group_name = form.cleaned_data['group_name']
            group_description = form.cleaned_data['group_description']
            created_group = Group(name=group_name)
            created_group.save()
            # create related group info
            created_group_info = GroupInfo(
                    group_description=group_description,
                    group=created_group)
            created_group_info.save()
            # relate user to group
            request.user.groups.add(created_group)
            # redirect to group page
            return redirect('group_page',
                            group_info_id=created_group_info.id)
    else:
        form = CreateGroupForm()
    render_data_dict = {
            'form': form,            
    }
    return render(request,
                  'group_info/create_group_page.html',
                  render_data_dict)

@login_required
def show_group_page(request, group_info_id):
    """
    recive GroupInfo id as the paremeter.
    """
    # authentication
    group_info = get_object_or_404(GroupInfo, id=int(group_info_id))
    if group_info.group not in request.user.groups.all():
        raise Http404
    if not group_info.real_group:
        raise Http404
    
    # extract infomation for rendering
    # extract user name list, should change to link when finished user page dev
    user_set = group_info.group.user_set
    user_name_list = [user.username for user in user_set.all()]
    render_data_dict = {
            'group_name': group_info.group.name,
            'group_description': group_info.group_description,
            'group_member': user_name_list,
    }
    return render(request, 
                  'group_info/group_page.html', 
                  render_data_dict)

@login_required
def show_group_list(request):
    """
    show groups related to the user
    """
    group_list = request.user.groups.all()
    group_info_list = [group.groupinfo for group in group_list]
    # construct dictionary for rendering
    display_groups = {}
    for group, group_info in zip(group_list, group_info_list):
        display_groups[group_info.id] = group.name
    return render(request, 
                  'group_info/group_list_page.html',
                  {'display_groups': display_groups})





