from __future__ import unicode_literals
from django.conf.urls import include, patterns, url

from real_group.views import GroupManagementPageOfManager
from real_group.views import GroupManagementPageOfMember
from real_group.views import GroupListPage
from real_group.views import GroupPage

urlpatterns = patterns('',
        url(r'^(?P<real_group_id>\d+)/$', 
            GroupPage.as_view(),
            name='group_page'),
        url(r'^list/$', 
            GroupListPage.as_view(),
            name='group_list_page'),
        # management page of manager
        url(r'^(?P<real_group_id>\d+)/manager_management/$', 
            GroupManagementPageOfManager.as_view(),
            name='group_management_page_of_manager'),
        # management page of member
        url(r'^(?P<real_group_id>\d+)/member_management/$', 
            GroupManagementPageOfMember.as_view(),
            name='group_management_page_of_member'),
        # manager delete user from group
        url(r'^delete_user/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/$',
            'real_group.views.manager_delete_user_from_group', 
            name='manager_delete_user_from_group'),
        # quit group
        url(r'^quit/(?P<real_group_id>\d+)/$',
            'real_group.views.user_quit_from_group', 
            name='user_quit_from_group'),

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
