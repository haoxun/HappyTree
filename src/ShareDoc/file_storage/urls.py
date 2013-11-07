from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from file_storage.views import CreateMessage
from file_storage.views import ModifyMessage

urlpatterns = patterns('',
    # modify message
    url(r'^modify/(?P<message_id>\d+)/$', 
        ModifyMessage.as_view(),
        name='modify_message'),
    # create message
    url(r'^create/$', 
        CreateMessage.as_view(),
        name='create_message'),
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
