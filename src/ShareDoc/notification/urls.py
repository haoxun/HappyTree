from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from notification.views import NotificationPage

urlpatterns = patterns('',
    url(r'^$', 
        NotificationPage.as_view(),
        name='notification_page'),
    url(r'process/user_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY|FINISH)/$',
        'notification.views.process_user_project_ac', 
        name='process_user_project_ac'),
    url(r'process/user_real_group/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY|FINISH)/$',
        'notification.views.process_user_real_group_ac', 
        name='process_user_real_group_ac'),
    url(r'process/real_group_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY|FINISH)/$',
        'notification.views.process_real_group_project_ac', 
        name='process_real_group_project_ac'),

)
