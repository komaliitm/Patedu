from django.conf.urls import patterns, url
from vaccination import views

urlpatterns = patterns('',
    url(r'^$', views.APIInfo, name='InformationofAPI'),
    url(r'^beneficiary/(.+)/$', views.RestBeneficiary, name='REST interface on beneficiary'),
    url(r'^beneficiary/$', views.RestBeneficiaryList, name='Get beneficiary list')
)