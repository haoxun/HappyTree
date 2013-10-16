from __future__ import unicode_literals
from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
        url(r'^create/$', 'real_group.views.create_group', name='create_group_page'),
        url(r'^(?P<real_group_id>\d+)/$', 'real_group.views.group_page', name='group_page'),
        url(r'^list/$', 'real_group.views.show_group_list', name='group_list_page'),
        url(r'^(?P<real_group_id>\d+)/management/$', 'real_group.views.show_group_management', name='group_management_page'),
        url(r'^delete_user/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/$',
            'real_group.views.delete_user_from_group', 
            name='delete_user_from_group'),
        url(r'^set_manager/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/$', 
            'real_group.views.set_manager_permission', 
            name='set_manager_permission'),
        url(r'^remove_manager/(?P<real_group_id>\d+)/(?P<user_info_id>\d+)/$', 
            'real_group.views.remove_manager_permission', 
            name='remove_manager_permission'),
        url(r'^(?P<real_group_id>\d+)/invite_user/(?P<user_info_id>\d+)/$', 
            'real_group.views.invite_user_to_real_group',
            name='invite_user_to_real_group'),
        url(r'^(?P<real_group_id>\d+)/apply_to_group/(?P<user_info_id>\d+)/$', 
            'real_group.views.user_apply_to_real_group',
            name='user_apply_to_real_group'),

)
