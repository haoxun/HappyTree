from __future__ import unicode_literals
from django.conf.urls import include, patterns, url

from real_group.views import GroupManagementPage

urlpatterns = patterns('',
        url(r'^create/$', 
            'real_group.views.create_group_page', 
            name='create_group_page'),
        url(r'^(?P<real_group_id>\d+)/$', 
            'real_group.views.group_page', 
            name='group_page'),
        url(r'^list/$', 
            'real_group.views.group_list_page', 
            name='group_list_page'),
        # class view test
        url(r'^(?P<real_group_id>\d+)/management/$', 
            GroupManagementPage.as_view(),
            name='group_management_page'),
        # delete user from group
        url(r'^delete_user/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/$',
            'real_group.views.delete_user_from_group', 
            name='delete_user_from_group'),
        # process user permission
        url(r'^process/user_permission/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/(?P<decision>True|False)/$', 
            'real_group.views.process_user_permission', 
            name='process_user_permission'),
        # RTU
        url(r'^(?P<real_group_id>\d+)/invite_user/(?P<user_info_id>\d+)/$', 
            'real_group.views.invite_user_to_real_group',
            name='invite_user_to_real_group'),
        # UTR
        url(r'^(?P<real_group_id>\d+)/apply_to_group/(?P<user_info_id>\d+)/$', 
            'real_group.views.user_apply_to_real_group',
            name='user_apply_to_real_group'),

)
