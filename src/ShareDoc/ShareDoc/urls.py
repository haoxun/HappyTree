from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.conf import settings

from user_info.views import HomePage
from entrance.views import Login

urlpatterns = patterns('',

    url(r'^$', HomePage.as_view(), name='home_page'),
    url(r'^login/$', Login.as_view(), name='login_page'),
    url(r'^logout/$', 'entrance.views.logout_user', name='logout_user'),
    url(r'^group/', include('real_group.urls')),
    url(r'^user/', include('user_info.urls')),
    url(r'^project/', include('project.urls')),
    url(r'^message/', include('message.urls')),
    url(r'^notification/', include('notification.urls')),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'test/$', 'debug_page.views.models_page'),
    )
