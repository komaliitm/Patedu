from __future__ import absolute_import
from celery import shared_task
from vaccination.models import Vaccinations

@shared_task
def add(x,y):
	return x+y

@shared_task
def add(x,y):
	return x+y

@shared_task
def dummy(x,y):
    v = Vaccinations('xyz', 12)
    v.save()