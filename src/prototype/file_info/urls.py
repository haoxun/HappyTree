from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'prototype.views.home', name='home'),
    # url(r'^prototype/', include('prototype.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^create/(?P<message_id>\d+)/$', 'file_info.views.create_message', name='create_message_page'),
    url(r'^create/(?P<message_id>\d+)/delete_file/(?P<file_info_id>\d+)/$', 
        'file_info.views.delete_file_from_message',
        name='delete_file_from_message'),
    url(r'^init/$', 'file_info.views.create_message', {'message_id': None}, name='init_message_page'),
    url(r'^list/$', 'file_info.views.show_project_related_message', name='project_message_page'),
    url(r'^download_file/(?P<file_info_id>\d+)/$', 'file_info.views.download_file', name='download_file'),
)

