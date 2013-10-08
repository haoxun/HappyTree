# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from group_info.models import GroupInfo
from .forms import GroupNameHandlerForm, GroupDescriptionHandlerForm, AddUserForm

@login_required
def create_group(request):
    if request.method == "POST":
        form_group_name = GroupNameHandlerForm(request.POST)    
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        if form_group_name.is_valid() and form_group_description.is_valid():
            # create group
            group_name = form_group_name.cleaned_data['group_name']
            group_description = \
                    form_group_description.cleaned_data['group_description']
            created_group = Group(name=group_name)
            created_group.save()
            # create related group info
            created_group_info = GroupInfo(
                    group_description=group_description,
                    group=created_group)
            created_group_info.save()
            # add user to group manager
            created_group_info.manager_user.add(request.user)
            # relate user to group
            request.user.groups.add(created_group)
            # redirect to group page
            return redirect('group_page',
                            group_info_id=created_group_info.id)
    else:
        form_group_name = GroupNameHandlerForm()    
        form_group_description = GroupDescriptionHandlerForm()
    render_data_dict = {
            'form_group_name': form_group_name,            
            'form_group_description': form_group_description,
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
    group_info_id = int(group_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    if group_info.group not in request.user.groups.all():
        raise Http404
    if not group_info.real_group:
        raise Http404
    
    # extract infomation for rendering
    # extract user name list, should change to link when finished user page dev
    user_set = group_info.group.user_set
    user_name_list = [user.username for user in user_set.all()]
    is_manager_user = True \
            if request.user in group_info.manager_user.all() else False
    render_data_dict = {
            'group_name': group_info.group.name,
            'group_description': group_info.group_description,
            'group_member': user_name_list,
            'is_manager_user': is_manager_user,
            'group_info_id': group_info_id,
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

@login_required
def show_group_management(request, group_info_id):
    """
    show management page of a group
    """
    # to int
    group_info_id = int(group_info_id)
    # authentication
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    group = group_info.group
    if request.user not in group_info.manager_user.all():
        raise Http404
    if group_info.group not in request.user.groups.all():
        raise Http404
    if not group_info.real_group:
        raise Http404
    
    # process form
    if request.method == 'POST':
        form_group_name = GroupNameHandlerForm(request.POST)
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        form_add_user = AddUserForm(request.POST)

        if form_group_name.is_valid():
            # update group info, short-circuit
            group_name = form_group_name.cleaned_data['group_name']
            group.name = group_name
            group.save()
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        # deal with the situation of empty description
        if form_group_description.is_valid() \
                and 'group_description' in request.POST: 
            # add user
            group_description = \
                    form_group_description.cleaned_data['group_description']
            group_info.group_description = group_description
            group_info.group_description.save()
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        if form_add_user.is_valid():
            username = form_add_user.cleaned_data['username']
            user = User.objects.get(username=username)
            group.user_set.add(user)
            return redirect('group_management_page',
                            group_info_id=group_info_id)

    else:
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = AddUserForm()

    # rendering    
    render_data_dict = {
            'form_group_name': form_group_name,            
            'form_group_description': form_group_description,
            'form_add_user': form_add_user,
            'group_info_id': group_info_id,
    }
    return render(request,
                  'group_info/group_management_page.html',
                  render_data_dict)







