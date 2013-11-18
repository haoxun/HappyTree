from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from message.views import AJAX_MessageWidget
from message.views import AJAX_SingleFile
from message.views import AJAX_FileList
from message.views import AJAX_HomePageMessageList
from message.views import AJAX_UserPageMessageList
from message.views import AJAX_ProjectPageMessageList

urlpatterns = patterns('',
    # message
    url(r'^$', 
        AJAX_MessageWidget.as_view(),
        name='message_widget'),
    # file of message
    url(r'^(?P<message_id>\d+)/file/$', 
        AJAX_SingleFile.as_view(),
        name='message_file'),
    # file list
    url(r'^(?P<message_id>\d+)/file_list/$', 
        AJAX_FileList.as_view(),
        name='message_file_list'),
    # message list of home page.
    url(r'^home_message_list/$', 
        AJAX_HomePageMessageList.as_view(),
        name='home_message_list'),
    # message list of user page
    url(r'^user_message_list/$', 
        AJAX_UserPageMessageList.as_view(),
        name='user_message_list'),
    # message list of project page
    url(r'^project_message_list/$', 
        AJAX_ProjectPageMessageList.as_view(),
        name='project_message_list'),

)
