from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from message.views import AJAX_MessageWidget
from message.views import AJAX_SingleFile
from message.views import AJAX_FileList

urlpatterns = patterns('',
    # REST message
    url(r'^$', 
        AJAX_MessageWidget.as_view(),
        name='message_widget'),
    # REST file of message
    url(r'^(?P<message_id>\d+)/file/$', 
        AJAX_SingleFile.as_view(),
        name='message_file'),
    # REST file list
    url(r'^(?P<message_id>\d+)/file_list/$', 
        AJAX_FileList.as_view(),
        name='message_list'),
)
