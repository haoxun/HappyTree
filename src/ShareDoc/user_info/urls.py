from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from user_info.views import UserPage 

urlpatterns = patterns('',
    # user info
    url(r'(?P<user_info_id>\d+)/$',
        UserPage.as_view(),
        name="user_page"),

)
