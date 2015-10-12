from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.http import HttpResponseRedirect
from mcts_transactions.views import DashboardPage, SubcenterPage, BlockPage, OutreachMonitoringPage, HomeRedirectPage, UploadReportsPage
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'patedu.views.home', name='home'),
    # url(r'^patedu/', include('patedu.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^vaccination/', include('vaccination.urls')),
    url(r'^urlpattern/', include('sms.urls')),
    url(r'^mctsdata/', include('mcts_data.urls')),
    url(r'^subcenter/', include('mcts_transactions.urls')),
    url(r'^$', HomeRedirectPage),
    url(r'^dashboard/$', DashboardPage),
    url(r'^dashboard/subcenter_report/$', SubcenterPage),
    url(r'^dashboard/block_report/$', BlockPage),
    url(r'^dashboard/outreach_monitoring_report/$', OutreachMonitoringPage),
    url(r'^dashboard/upload_reports_page/$', UploadReportsPage),
    url(r'^login/', include('mcts_identities.urls'))
)
