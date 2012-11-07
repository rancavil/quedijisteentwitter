from django.conf.urls import patterns, include, url

# Administracion activada
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^tweets/',include('tweets.urls')),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
