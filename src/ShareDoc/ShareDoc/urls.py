from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.conf import settings

from user_info.views import HomePage

urlpatterns = patterns('',

    url(r'^$', HomePage.as_view(), name='home_page'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login_page'),
    url(r'^logout/$', 'user_info.views.logout_user', name='logout_user'),
    url(r'^group/', include('real_group.urls')),
    url(r'^apply_confirm/', include('user_info.urls')),
    url(r'^project/', include('project.urls')),
    url(r'^message/', include('file_storage.urls')),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'test/$', 'user_info.views.models_page'),
    )
