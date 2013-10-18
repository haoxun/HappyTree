from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ShareDoc.views.home', name='home'),
    # url(r'^ShareDoc/', include('ShareDoc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # init message
    url(r'^init/$', 
        'file_storage.views.init_message_page', 
        name='init_message_page'),
    # create message 
    url(r'^(?P<message_id>\d+)/create/$', 
        'file_storage.views.create_message_page', 
        name='create_message_page'),
    # delete message
    url(r'^(?P<message_id>\d+)/delete/$', 
        'file_storage.views.delete_message', 
        name='delete_message'),
    # delete file of message
    url(r'^delete_file/(?P<file_pointer_id>\d+)/$', 
        'file_storage.views.delete_file_pointer_from_message', 
        name='delete_file_pointer_from_message'),
    # download file
    url(r'^download_file/(?P<file_pointer_id>\d+)/$', 
        'file_storage.views.download_file', 
        name='download_file'),

    
    
)
