from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ShareDoc.views.home', name='home'),
    # url(r'^ShareDoc/', include('ShareDoc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'user_info.views.home_page', name='home_page'),
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
