from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from mcts_data import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^uploadandsave/$', views.UploadAndSave),
	url(r'^uploadpage/$', views.UploadPage),
	url(r'^uploadandsaveLangLatData/$', views.uploadandsaveLangLatData),
	url(r'^uploadLangLatpage/$', views.uploadLangLatpage),
	url(r'^$', views.MctsPage)
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)