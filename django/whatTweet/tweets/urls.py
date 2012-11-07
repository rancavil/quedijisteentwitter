# URLS personalizadas para la aplicacion,esta es referenciada desde whatTweet/whatTweet/urls.py
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('tweets.views',
    url(r'^$','index'),
    (r'^topfive/$','topfive'),
    (r'^tweets/$','tweets'),
)

urlpatterns += staticfiles_urlpatterns()
