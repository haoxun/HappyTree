from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
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
from project.forms import RealGroupApplyToProjectForm
# decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# util
from ShareDoc.utils import url_with_querystring, extract_from_GET
from real_group.utils import construct_user_real_group_ac
# python library
from datetime import datetime
import json

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

class GroupManagementPage(View):
    """
    This class manage the process logic of group management page.
    """
    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('real_group_management', 
                      (RealGroup, 'id', 'real_group_id',)))
    def dispatch(self, *args, **kwargs):
        return super(GroupManagementPage, self).dispatch(*args, **kwargs)

    def get(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        # form
        form_group_name = GroupNameHandlerForm()
        form_group_description = GroupDescriptionHandlerForm()
        form_add_user = AddUserForm()
        form_apply_to_project = RealGroupApplyToProjectForm()
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
    
    # form process, base on AJAX POST.
    def _group_info_handler(self, request, real_group, form_cls, field_name):
        form = form_cls(request.POST)
        if form.is_valid():
            field = form.cleaned_data[field_name]
            setattr(real_group, field_name, field)
            real_group.save()
            json_data = json.dumps({
                            'error': False,
                            'data' : {field_name: field},
                        })
            return HttpResponse(json_data, content_type='application/json')
        else:
            errors_dict = dict(form.errors)
            for key, value in errors_dict.items():
                errors_dict[key] = "; ".join(value)
            json_data = json.dumps({
                            'error': True,
                            'data': errors_dict,
                        })
            return HttpResponse(json_data, content_type='application/json')
    
    def _apply_confirm_handler(self, 
                               request, 
                               real_group, 
                               form_cls,
                               target_set_generator):
        form = form_cls(request.POST)
        if form.is_valid():
            target_set = target_set_generator(form, real_group)
            json_data = json.dumps({
                            'error': False,
                            'data': target_set,
                        })
            return HttpResponse(json_data, content_type='application/json')
        else:
            errors_dict = dict(form.errors)
            for key, value in errors_dict.items():
                errors_dict[key] = "; ".join(value)
            json_data = json.dumps({
                            'error': errors_dict,
                        })
            return HttpResponse(json_data, content_type='application/json')

    def _add_user_generator(self, form_add_user, real_group):
        add_user_set = {}
        for user in form_add_user.add_user_set:
            if user.has_perm('real_group_membership', real_group):
                # already in group, not display
                continue
            keywords = {'real_group_id': real_group.id,
                        'user_info_id': user.userinfo.id}
            add_user_set[user.username] = \
                    reverse('invite_user_to_real_group',
                            kwargs=keywords)
        return add_user_set
    
    def _add_project_set(self, form_apply_to_project, real_group):
        add_project_set = {}
        for project in form_apply_to_project.add_project_set:
            keywords = {'real_group_id': real_group.id,
                        'project_id': project.id}
            add_project_set[project.name] = \
                    reverse('real_group_apply_to_project',
                            kwargs=keywords)
        return add_project_set

    def _gen_handler(self, request):
        if "group_name_submit" in request.POST:
            return self._group_name_handler
        elif "group_description_submit" in request.POST:
            return self._group_description_handler
        elif "RTU_submit" in request.POST:
            return self._real_group_apply_to_user_handler
        elif "RTP_submit" in request.POST:
            return self._real_group_apply_to_project_handler
        else:
            raise PermissionDenied

    def _group_name_handler(self, request, real_group):
        return self._group_info_handler(request, 
                                        real_group, 
                                        GroupNameHandlerForm,
                                        'name')
    
    def _group_description_handler(self, request, real_group):
        return self._group_info_handler(request, 
                                        real_group, 
                                        GroupDescriptionHandlerForm,
                                        'description')

    def _real_group_apply_to_user_handler(self, request, real_group):
        return self._apply_confirm_handler(request,
                                           real_group,
                                           AddUserForm,
                                           self._add_user_generator)
    def _real_group_apply_to_project_handler(self, request, real_group):
        return self._apply_confirm_handler(request,
                                           real_group,
                                           RealGroupApplyToProjectForm,
                                           self._add_project_set)

    def post(self, request, real_group_id):
        real_group = get_object_or_404(RealGroup, id=int(real_group_id))
        handler = self._gen_handler(request)
        return handler(request, real_group)

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
    

