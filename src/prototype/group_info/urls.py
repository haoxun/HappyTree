from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
        url(r'^create_group/$', 'group_info.views.create_group', name='create_group_page'),
        url(r'^(?P<group_info_id>\d+)/info/$', 'group_info.views.show_group_page', name='group_page'),
        url(r'^list/$', 'group_info.views.show_group_list', name='group_list_page'),
        url(r'^(?P<group_info_id>\d+)/management/$', 'group_info.views.show_group_management', name='group_management_page'),
        url(r'^management/delete_user/$', 'group_info.views.delete_user_from_group', name='delete_user_from_group'),
        url(r'^management/remove_manager/$', 'group_info.views.remove_user_from_group_manager', name='delete_manager_from_group'),

)
