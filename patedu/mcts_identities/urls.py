from django.conf.urls import patterns, url
from mcts_identities.views import login_page, login_user, logout_user 

urlpatterns = patterns('',
    url(r'^$', login_page, name='html page for login'),
    url(r'^login_user/$', login_user, name='Login api'),
    url(r'^logout_user/$', logout_user, name='logout api')
)