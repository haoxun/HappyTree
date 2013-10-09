from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'prototype.views.home', name='home'),
    # url(r'^prototype/', include('prototype.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'user_status.views.show_root', name='root_page'),
    url(r'status/', include('user_status.urls')),
    url(r'group/', include('group_info.urls')),
    url(r'project/', include('project_info.urls')),
)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'test/$', 'user_status.views.show_models'),
        )

