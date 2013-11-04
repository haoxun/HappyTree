from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from project.views import ProjectManagementPage
from project.views import ProjectListPage
from project.views import ProjectFileListPage
from project.views import ProjectMessagePage

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ShareDoc.views.home', name='home'),
    # url(r'^ShareDoc/', include('ShareDoc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # class view project lsit
    url(r'^list/$', 
        ProjectListPage.as_view(),
        name='project_list_page'),
    # show message related to project
    url(r'^(?P<project_id>\d+)/message_list/$', 
        ProjectMessagePage.as_view(),
        name='project_message_page'),
    # show files related to porject
    url(r'^(?P<project_id>\d+)/file_list/$', 
        ProjectFileListPage.as_view(),
        name='project_file_list_page'),
    # class view management page
    url(r'^management/(?P<project_id>\d+)/$', 
        ProjectManagementPage.as_view(),
        name='project_management_page'),
    # change role of user
    url(r'^process/user_role/(?P<project_id>\d+)/(?P<user_info_id>\d+)/(?P<decision>True|False)/$', 
        'project.views.process_user_role_on_project',
        name='process_user_role_on_project'),
    # delete user from project
    url(r'^process/delete_user/(?P<project_id>\d+)/(?P<user_info_id>\d+)/$', 
        'project.views.delete_user_from_project',
        name='delete_user_from_project'),
    # process exception on user'^s permission
    url(r'^process/user_permission/(?P<project_id>\d+)/(?P<user_info_id>\d+)/(?P<kind>download|upload|delete)/(?P<decision>True|False)/$', 
        'project.views.process_user_permission_on_project',
        name='process_user_permission_on_project'),
    # change default permissions of project
    url(r'^process/default_permission/(?P<project_id>\d+)/(?P<kind>download|upload|delete)/(?P<decision>True|False)/$', 
        'project.views.process_default_permission_on_project',
        name='process_default_permission_on_project'),
    # invite user to project
    url(r'^process/invite_user_to_project/(?P<project_id>\d+)/(?P<user_info_id>\d+)/$', 
        'project.views.invite_user_to_project',
        name='invite_user_to_project'),
    # invite real group to project
    url(r'^process/invite_real_group_to_project/(?P<project_id>\d+)/(?P<real_group_id>\d+)/$', 
        'project.views.invite_real_group_to_project',
        name='invite_real_group_to_project'),
    # user apply to project
    url(r'^process/user_apply_to_project/(?P<project_id>\d+)/(?P<user_info_id>\d+)/$', 
        'project.views.user_apply_to_project',
        name='user_apply_to_project'),
    # real group apply to project
    url(r'^process/real_group_apply_to_project/(?P<real_group_id>\d+)/(?P<project_id>\d+)/$', 
        'project.views.real_group_apply_to_project',
        name='real_group_apply_to_project'),


    
)


