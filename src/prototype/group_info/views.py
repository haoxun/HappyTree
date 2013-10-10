# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from user_status.models import UserInfo
from group_info.models import GroupInfo
from .forms import GroupNameHandlerForm, GroupDescriptionHandlerForm, AddUserForm
from .utils import url_with_querystring, check_user_in_group_manager, \
                   extract_from_GET
from .decorators import require_user_in_group_with_actor, set_group_info_id_from_GET_to_kwargs

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
@require_user_in_group_with_actor(actor='normal_user', flag=True)
def show_group_page(request, group_info_id):
    """
    recive GroupInfo id as the paremeter.
    """
    group_info_id = int(group_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    # extract infomation for rendering
    # extract user name list, should change to link when finished user page dev
    user_set = group_info.group.user_set
    manager_user = group_info.manager_user
    user_name_list = [user.username for user in user_set.all()]
    manager_name_list = [manager.username for manager in manager_user.all()]
    is_manager_user = True \
            if group_info.manager_user.filter(username=request.user.username) \
                else False
    render_data_dict = {
            'group_name': group_info.group.name,
            'group_description': group_info.group_description,
            'group_manager': manager_name_list,
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
        # only display the 'real' group
        if group_info.real_group:
            display_groups[group_info.id] = group.name
    return render(request, 
                  'group_info/group_list_page.html',
                  {'display_groups': display_groups})

@login_required
@require_user_in_group_with_actor(actor='manager_user', flag=True)
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
            group_info.save()
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        if form_add_user.is_valid():
            username = form_add_user.cleaned_data['username']
            user = User.objects.get(username=username)
            group.user_set.add(user)
            return redirect('group_management_page',
                            group_info_id=group_info_id)

        if form_add_manager.is_valid():
            username = form_add_manager.cleaned_data['username']
            user = User.objects.get(username=username)
            if user not in group.user_set.all():
                form_add_manager._errors = {
                        'username': [u'{} not in the group!'.format(username)], 
                }
            else:
                group_info.manager_user.add(user)
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
    manager_user_set = group_info.manager_user.all()
    group_manager = {}
    for manager_user in manager_user_set:
        query = {
            'group_info_id': group_info_id,
            'user_info_id': manager_user.id,
        }
        group_manager[manager_user.username] = url_with_querystring(
                                                    remove_manager_url, 
                                                    **query)
    # user
    remove_user_url = reverse('delete_user_from_group')
    normal_user_set = group.user_set.all()
    group_user = {}
    for normal_user in normal_user_set:
        query = {
            'group_info_id': group_info_id,
            'user_info_id': normal_user.userinfo.id,
        }
        group_user[normal_user.username] = url_with_querystring(
                                                remove_user_url,
                                                **query)
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
@set_group_info_id_from_GET_to_kwargs
@require_user_in_group_with_actor(actor='manager_user', flag=True)
def delete_user_from_group(request, *args, **kwargs):
    # authentication
    group_info_id, user_info_id = extract_from_GET(request.GET)
    delete_user_info = get_object_or_404(UserInfo, id=user_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    # manager can not be remove from group
    check_user_in_group_manager(delete_user_info.user, group_info, False)
    # delete user
    group_info.group.user_set.remove(delete_user_info.user)
    return redirect('group_management_page',
                    group_info_id=group_info_id)

@login_required
@set_group_info_id_from_GET_to_kwargs
@require_user_in_group_with_actor(actor='manager_user', flag=True)
def remove_user_from_group_manager(request, *args, **kwargs):
    # authentication
    group_info_id, user_info_id = extract_from_GET(request.GET)
    delete_user_info = get_object_or_404(UserInfo, id=user_info_id)
    group_info = get_object_or_404(GroupInfo, id=group_info_id)
    # manager can not be remove from group
    check_user_in_group_manager(delete_user_info.user, group_info, True)
    # remove manager
    if group_info.manager_user.count() > 1:
        group_info.manager_user.remove(delete_user_info.user)
    else:
        raise Http404
    return redirect('group_management_page',
                    group_info_id=group_info_id)
