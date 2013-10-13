from __future__ import unicode_literals
# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_info.models import UserInfo
from group_info.models import GroupInfo
from .forms import GroupNameHandlerForm, GroupDescriptionHandlerForm, AddUserForm
from prototype.utils import url_with_querystring, extract_from_GET
from prototype.decorators import require_user_in
from .utils import judge_func, assert_user_in_group_manager, \
                   assert_user_not_in_group_manager

from datetime import datetime

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

            # group name must be unique!
            # use user name + created time as group name
            unique_group_name = "".join(('[real]', 
                                         request.user.username, 
                                         unicode(datetime.now())))
            group = Group(name=unique_group_name)
            group.save()
            # create related group info to handle group information
            group_info = GroupInfo(name=group_name,
                                   description=group_description,
                                   group=group,
                                   owner=request.user)
            group_info.save()
            # add user to group manager
            group_info.manager.add(request.user)
            # relate user to group
            request.user.groups.add(group)
            # redirect to group page
            return redirect('group_page',
                            group_info_id=group_info.id)
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
@require_user_in(
        judge_func, 
        'group_info_id', 
        (GroupInfo, True, ('group', 'user_set'))
)
def show_group_page(request, group_info_id):
    """
    recive GroupInfo id as the paremeter.
    """
    group_info_id = int(group_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    group = group_info.group
    # extract infomation for rendering
    # extract user name list, should change to link when finished user page dev
    user_set = group.user_set
    manager_set = group_info.manager
    user_name_list = [user.username for user in user_set.all()]
    manager_name_list = [manager.username for manager in manager_set.all()]
    is_manager = True \
            if group_info.manager.filter(username=request.user.username) \
                else False
    render_data_dict = {
            'group_name': group_info.name,
            'group_description': group_info.description,
            'group_manager': manager_name_list,
            'group_member': user_name_list,
            'is_manager': is_manager,
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
    # construct dictionary for rendering
    display_groups = {}
    for group in group_list:
        # only display the 'real' group
        group_info = group.groupinfo
        if group_info.real_flag:
            display_groups[group_info.id] = group_info.name
    return render(request, 
                  'group_info/group_list_page.html',
                  {'display_groups': display_groups})

@login_required
@require_user_in(
        judge_func, 
        'group_info_id', 
        (GroupInfo, True, ('manager',))
)
def show_group_management(request, group_info_id):
    """
    show management page of a group
    """
    # to int
    group_info_id = int(group_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    group = group_info.group
    
    # process form
    if request.method == 'POST':
        form_group_name = GroupNameHandlerForm(request.POST)
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        form_add_user = AddUserForm(request.POST, prefix='normal')
        form_add_manager = AddUserForm(request.POST, prefix='manager')

        if form_group_name.is_valid():
            # update group info, short-circuit
            group_name = form_group_name.cleaned_data['group_name']
            group_info.name = group_name
            group_info.save()
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        # deal with the situation of empty description
        if form_group_description.is_valid():
            # add user
            group_description = \
                    form_group_description.cleaned_data['group_description']
            group_info.description = group_description
            group_info.save()
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        if form_add_user.is_valid():
            username = form_add_user.cleaned_data['username']
            user = get_object_or_404(User, username=username)
            group.user_set.add(user)
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        if form_add_manager.is_valid():
            username = form_add_manager.cleaned_data['username']
            user = get_object_or_404(User, username=username)
            if not group.user_set.filter(username=user.username):
                form_add_manager._errors = {
                        'username': [u'{} not in the group!'.format(username)], 
                }
            else:
                group_info.manager.add(user)
                return redirect('group_management_page',
                                group_info_id=group_info_id)

    else:
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = AddUserForm(prefix='normal')
        form_add_manager = AddUserForm(prefix='manager')
    
    # process link
    # manager
    remove_manager_url = reverse('delete_manager_from_group')
    manager_set = group_info.manager.all()
    group_manager = {}
    for manager in manager_set:
        query = {
            'group_info_id': group_info_id,
            'user_info_id': manager.id,
        }
        group_manager[manager.username] = url_with_querystring(
                                                    remove_manager_url, 
                                                    **query)
    # user
    remove_user_url = reverse('delete_user_from_group')
    group_user = {}
    for user in group.user_set.all():
        query = {
            'group_info_id': group_info_id,
            'user_info_id': user.userinfo.id,
        }
        group_user[user.username] = url_with_querystring(
                                                remove_user_url,
                                                **query)
    # exclusive operation
    for name, remove_url in group_manager.items():
        if name in group_user:
            group_user[name] = None
    # forbid remove if there's only one manager in the group
    if len(group_manager) == 1:
        for name in group_manager:
            group_manager[name] = None

    # rendering    
    render_data_dict = {
            'form_group_name': form_group_name,            
            'form_group_description': form_group_description,
            'form_add_user': form_add_user,
            'group_info_id': group_info_id,
            'form_add_manager': form_add_manager,
            'group_manager': group_manager,
            'group_user': group_user,
    }
    return render(request,
                  'group_info/group_management_page.html',
                  render_data_dict)

@login_required
@require_user_in(
        judge_func, 
        'group_info_id', 
        (GroupInfo, True, ('manager',))
)
def delete_user_from_group(request, *args, **kwargs):
    # authentication
    group_info_id, user_info_id = extract_from_GET(
            request.GET, 
            'group_info_id', 'user_info_id')
    delete_user_info = get_object_or_404(UserInfo, id=user_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    # manager can not be remove from group
    assert_user_not_in_group_manager(delete_user_info.user, group_info)
    # delete user
    group_info.group.user_set.remove(delete_user_info.user)
    return redirect('group_management_page',
                    group_info_id=group_info_id)

@login_required
@require_user_in(
        judge_func, 
        'group_info_id', 
        (GroupInfo, True, ('manager',))
)
def remove_user_from_group_manager(request, *args, **kwargs):
    # authentication
    group_info_id, user_info_id = extract_from_GET(
            request.GET,
            'group_info_id', 'user_info_id')
    delete_user_info = get_object_or_404(UserInfo, id=user_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    # manager can not be remove from group
    assert_user_in_group_manager(delete_user_info.user, group_info)
    # remove manager
    if group_info.manager.count() > 1:
        group_info.manager.remove(delete_user_info.user)
    else:
        raise Http404
    return redirect('group_management_page',
                    group_info_id=group_info_id)
