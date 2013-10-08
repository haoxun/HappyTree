# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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
            created_group_info = GroupInfo(group_description=group_description,
                                           group=created_group)
            created_group_info.save()
            # relate user to group
            request.user.groups.add(created_group)
            # redirect to group page
            pass
    else:
        form = CreateGroupForm()
    return render(request, 'group_info/create_group_page.html', 
                  {'form' : form})

