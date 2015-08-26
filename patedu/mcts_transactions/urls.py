from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from mcts_transactions import views
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^dashboard/$', views.DashboardPage),
	url(r'^dashboard/data/(\d+)/$', views.DashboardData),
	url(r'^dashboard/data/$', views.DashboardData),
	url(r'^wp_call/ods/anm/$', views.ODSANMANC),
	url(r'^dashboard/workplan/$', views.SubcWorkplan)
)