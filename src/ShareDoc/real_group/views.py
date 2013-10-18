from __future__ import unicode_literals
# django dependency
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from guardian.decorators import permission_required_or_403, permission_required
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms, \
                               get_objects_for_user
# model 
from guardian.models import User, Group
from user_info.models import UserInfo
from real_group.models import RealGroup, UserInfo_RealGroup_AC
# form
from real_group.forms import GroupNameHandlerForm, GroupDescriptionHandlerForm, \
                             AddUserForm, ApplyToGroupForm
from project.forms import RealGroupApplyToForm
# decorator
from django.contrib.auth.decorators import login_required
# util
from ShareDoc.utils import url_with_querystring, extract_from_GET
from real_group.utils import construct_user_real_group_ac
# python library
from datetime import datetime

@login_required
def create_group_page(request):
    if request.method == "POST":
        form_group_name = GroupNameHandlerForm(request.POST)    
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        if form_group_name.is_valid() and form_group_description.is_valid():
            # create group
            name = form_group_name.cleaned_data['name']
            description = \
                    form_group_description.cleaned_data['description']
            # use user name + created time as group name
            unique_name = (
                    '[real]',
                    request.user.username,
                    unicode(datetime.now()),
            )
            unique_name = "".join(unique_name)
            group = Group.objects.create(name=unique_name)
            # create related group info to handle group information
            real_group = RealGroup.objects.create(name=name,
                                                  description=description,
                                                  group=group)
            # set group's management permission to user
            assign_perm('real_group_ownership', request.user, real_group)
            assign_perm('real_group_management', request.user, real_group)
            assign_perm('real_group_membership', request.user, real_group)

            # relate user to group
            group.user_set.add(request.user)
            # redirect to group page
            return redirect('group_page',
                            real_group_id=real_group.id)
    else:
        form_group_name = GroupNameHandlerForm()    
        form_group_description = GroupDescriptionHandlerForm()
    render_data_dict = {
            'form_group_name': form_group_name,            
            'form_group_description': form_group_description,
    }
    return render(request,
                  'real_group/create_group_page.html',
                  render_data_dict)

@permission_required_or_403('real_group_membership', (RealGroup, 'id', 'real_group_id',))
def group_page(request, real_group_id):
    """
    recive RealGroup id as the paremeter.
    """
    real_group_id = int(real_group_id)
    real_group = get_object_or_404(RealGroup, id=real_group_id)
    user_set = get_users_with_perms(real_group)

    render_data_dict = {
            'request': request,
            'real_group': real_group,
            'user_set': user_set,
    }
    return render(request, 
                  'real_group/group_page.html', 
                  render_data_dict)

@login_required
def group_list_page(request):
    """
    show groups related to the user
    """
    if request.method == "POST":
        form_apply_to_group = ApplyToGroupForm(request.POST)
    else:
        form_apply_to_group = ApplyToGroupForm()

    real_group_set = get_objects_for_user(request.user, 
                                          'real_group.real_group_membership')
    render_data_dict = {
            'request': request,
            'real_group_set': real_group_set,
            'form_apply_to_group': form_apply_to_group,
    }

    return render(request, 
                  'real_group/group_list_page.html',
                  render_data_dict)

@permission_required_or_403('real_group_management', (RealGroup, 'id', 'real_group_id',))
def group_management_page(request, real_group_id):
    """
    show management page of a group
    """
    real_group_id = int(real_group_id)
    real_group = get_object_or_404(RealGroup, id=real_group_id)
    group = real_group.group
    if request.method == 'POST':
        # build form with data
        form_group_name = GroupNameHandlerForm(request.POST)
        form_group_description = GroupDescriptionHandlerForm(request.POST)
        form_add_user = AddUserForm(request.POST)
        form_apply_to_project = RealGroupApplyToForm(request.POST)

        if form_group_name.is_valid():
            # update group info, short-circuit
            name = form_group_name.cleaned_data['name']
            real_group.name = name
            real_group.save()
            return redirect('group_management_page',
                            real_group_id=real_group_id)

        # deal with the situation of empty description
        if form_group_description.is_valid():
            # add user
            description = form_group_description.cleaned_data['description']
            real_group.description = description
            real_group.save()
            return redirect('group_management_page',
                            real_group_id=real_group_id)

        if form_add_user.is_valid():
            # unbound name, description
            form_group_name = GroupNameHandlerForm()
            form_group_description = GroupDescriptionHandlerForm()
            form_apply_to_project = RealGroupApplyToForm()

        if form_apply_to_project.is_valid():
            form_group_name = GroupNameHandlerForm()
            form_group_description = GroupDescriptionHandlerForm()
            form_add_user = AddUserForm()


    else:
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = AddUserForm()
        form_apply_to_project = RealGroupApplyToForm()
    
    # rendering    
    render_data_dict = {
            'request': request,
            'form_group_name': form_group_name,            
            'form_group_description': form_group_description,
            'form_apply_to_project': form_apply_to_project,
            'form_add_user': form_add_user,
            'real_group': real_group,
            'user_set': get_users_with_perms(real_group),
    }
    return render(request,
                  'real_group/group_management_page.html',
                  render_data_dict)


@permission_required_or_403('real_group_management', (RealGroup, 'id', 'real_group_id',))
def invite_user_to_real_group(request, user_info_id, real_group_id):
    construct_user_real_group_ac(user_info_id, real_group_id, "ACTION_RTU")
    return redirect('group_management_page',
                    real_group_id=int(real_group_id))

@login_required
def user_apply_to_real_group(request, user_info_id, real_group_id):
    construct_user_real_group_ac(user_info_id, real_group_id, "ACTION_UTR")
    return redirect('group_list_page')

@permission_required_or_403('real_group_management', (RealGroup, 'id', 'real_group_id',))
def delete_user_from_group(request, real_group_id, user_info_id):
    real_group_id = int(real_group_id)
    user_info_id = int(user_info_id)
    # authentication
    user = get_object_or_404(UserInfo, id=user_info_id).user
    real_group = get_object_or_404(RealGroup, id=real_group_id)
    # manager can not be remove from group
    if user.has_perm('real_group_ownership', real_group) \
            or user.has_perm('real_group_management', real_group):
        raise PermissionDenied
    # delete user
    real_group.group.user_set.remove(user)
    remove_perm('real_group_membership', user, real_group)
    return redirect('group_management_page',
                    real_group_id=real_group_id)

@permission_required_or_403('real_group_management', (RealGroup, 'id', 'real_group_id',))
def process_user_permission(request, real_group_id, user_info_id, decision):
    if decision == "True":
        tack_action = assign_perm
    elif decision == "False":
        tack_action = remove_perm
    else:
        raise PermissionDenied
    user = get_object_or_404(UserInfo, id=int(user_info_id)).user
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    tack_action('real_group_management', user, real_group)
    return redirect('group_management_page',
                    real_group_id=real_group_id)
    

