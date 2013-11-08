from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.views.generic.base import View
from django.shortcuts import render
# auth dependency
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403
from guardian.decorators import permission_required
# model
# form
# decorator
from django.utils.decorators import method_decorator
# util
from notification.utils import NotificationCenter
from notification.utils import ProcessUserProjectAC
from notification.utils import ProcessUserRealGroupAC
from notification.utils import ProcessRealGroupProjectAC
# python library
import operator
import re


class NotificationPage(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NotificationPage, self).dispatch(*args, **kwargs)

    def get(self, request):
        return render(request,
                      'notification/ac_list.html')

    def post(self, request):
        notification_center = NotificationCenter(request.user)
        return HttpResponse(notification_center.notification_html)


@login_required
def process_user_project_ac(request, ac_id, decision):
    ac_processor = ProcessUserProjectAC(request, ac_id, decision)
    ac_processor.handle()

    return HttpResponse('OK')


@login_required
def process_user_real_group_ac(request, ac_id, decision):
    ac_processor = ProcessUserRealGroupAC(request, ac_id, decision)
    ac_processor.handle()

    return HttpResponse('OK')


@login_required
def process_real_group_project_ac(request, ac_id, decision):
    ac_processor = ProcessRealGroupProjectAC(request, ac_id, decision)
    ac_processor.handle()

    return HttpResponse('OK')
