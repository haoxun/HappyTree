from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.http import HttpResponseRedirect 
from django.views.generic.base import View
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.context_processors import csrf
# auth dependency
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup 
# form
from entrance.forms import LoginForm
# decorator
from django.utils.decorators import method_decorator
# util
# python library


class Login(View):
    def get(self, request):
        redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '/')
        if request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to)

        form = LoginForm()
        render_data_dict = {
            'form': form,
            'next': redirect_to,
        }
        render_data_dict.update(csrf(request))
        return render(request,
                      'entrance/login.html',
                      render_data_dict)

    def post(self, request):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        redirect_to = request.POST.get('next', '/')
        if email is None or password is None:
            raise PermissionDenied
        # get user name
        username = get_object_or_404(UserInfo, email=email).user.username
        user = authenticate(username=username, password=password)
        if user is not None:
            print "good"
            login(request, user)
            return HttpResponse(redirect_to)
        else:
            pass


@login_required
def logout_user(request):
    logout(request)
    return redirect('login_page')
