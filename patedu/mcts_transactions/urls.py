from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from mcts_transactions import views
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^dashboard/$', views.DashboardPage),
	url(r'^dashboard/subcenter_report/$', views.SubcenterPage),
	url(r'^dashboard/block_report/$', views.BlockPage),
	url(r'^dashboard/outreach_monitoring_report/$', views.OutreachMonitoringPage),
	url(r'^dashboard/block_report/data/$', views.BlockIndicesData),
	url(r'^dashboard/outreach/data/$', views.OutreachData),
	url(r'^dashboard/data/(\d+)/$', views.DashboardData),
	url(r'^dashboard/data/$', views.DashboardData),
	url(r'^wp_call/ods/anm/$', views.ODSANMANC),
	url(r'^wp_call/services/count/$', views.ServicesCount),
	url(r'^dashboard/workplan/$', views.SubcWorkplan)
)