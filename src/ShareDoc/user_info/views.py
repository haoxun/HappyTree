from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.views.generic.base import View
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403
from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup 
# form
# decorator
from django.utils.decorators import method_decorator
from common.utils import POSTHandler
from user_info.utils import AJAX_HomePageHandler
from user_info.utils import AJAX_UserPageHandler
# util
# python library
import operator
import re


class HomePage(AJAX_HomePageHandler, POSTHandler):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomePage, self).dispatch(*args, **kwargs)

    def get(self, request):
        return render(request,
                      'user_info/home.html')
                      
    def post(self, request):
        return self._handler(request)


class UserPage(AJAX_UserPageHandler, POSTHandler):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserPage, self).dispatch(*args, **kwargs)

    def get(self, request, user_info_id):
        user_info = get_object_or_404(UserInfo, id=int(user_info_id))
        return render(request,
                      'user_info/user_page.html',
                      {'user_info': user_info})

    def post(self, request, user_info_id):
        user_info = get_object_or_404(UserInfo, id=int(user_info_id))
        return self._handler(request, user_info)
