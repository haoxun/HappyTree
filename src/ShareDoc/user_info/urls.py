from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

from user_info.views import ApplyConfirmPage

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ShareDoc.views.home', name='home'),
    # url(r'^ShareDoc/', include('ShareDoc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 
        ApplyConfirmPage.as_view(),
        name='ac_page'),
    url(r'process/user_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_user_project_ac', 
        name='process_user_project_ac'),
    url(r'process/user_real_group/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_user_real_group_ac', 
        name='process_user_real_group_ac'),
    url(r'process/real_group_project/(?P<ac_id>\d+)/(?P<decision>ACCEPT|DENY)/$',
        'user_info.views.process_real_group_project_ac', 
        name='process_real_group_project_ac'),

)
