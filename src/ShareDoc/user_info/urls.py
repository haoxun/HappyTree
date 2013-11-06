from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from user_info.views import ApplyConfirmPage
from user_info.views import UserPage 

urlpatterns = patterns('',
    # gravatar test
    url(r'gravatar/(?P<email>(\w|\W)+)/$',
        'user_info.views.user_image_test'),
    # user info
    url(r'(?P<user_info_id>\d+)/$',
        UserPage.as_view(),
        name="user_page"),
    # ACs
    url(r'apply_confirm/$', 
        ApplyConfirmPage.as_view(),
        name='ac_page'),
    url(r'apply_confirm/process/user_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_user_project_ac', 
        name='process_user_project_ac'),
    url(r'apply_confirm/process/user_real_group/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_user_real_group_ac', 
        name='process_user_real_group_ac'),
    url(r'apply_confirm/process/real_group_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_real_group_project_ac', 
        name='process_real_group_project_ac'),

)
