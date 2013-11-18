from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from message.views import CreateMessage
from message.views import ModifyMessage
from message.views import AJAX_MessageWidget

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
        'message.views.delete_message', 
        name='delete_message'),
    # delete file of message
    url(r'^delete_file/(?P<file_pointer_id>\d+)/$', 
        'message.views.delete_file_pointer_from_message', 
        name='delete_file_pointer_from_message'),
    # download file
    url(r'^download_file/(?P<file_pointer_id>\d+)/$', 
        'message.views.download_file', 
        name='download_file'),
    # REST message
    url(r'^rest/$', 
        AJAX_MessageWidget.as_view(),
        name='ajax_mw'),
    

)
