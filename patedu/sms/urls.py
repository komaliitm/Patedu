from django.conf.urls import patterns, url
from sms import views

urlpatterns = patterns('',
    url(r'^$', views.ReplyResponse, name='ReplyResponse'),
)