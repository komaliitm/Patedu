from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# -*- coding: utf-8 -*-

class Document(models.Model):
    myfile = models.FileField(upload_to='mcts/media')
    stamp = models.CharField(max_length=256)

class AvailableMCTSData(models.Model):
	stamp = models.CharField(max_length=256)
	block = models.CharField(max_length=32)
	district = models.CharField(max_length=32)
	health_facility = models.CharField(max_length=32)
	month = models.CharField(max_length=10)
	year = models.CharField(max_length=10)
	state = models.CharField(max_length=32)
	subfacility = models.CharField(max_length=32)
	subfacility_id = models.CharField(max_length=10)
	benef_type = models.CharField(max_length=10)

class LatLangData(models.Model):
	lat = models.FloatField(null=True)
	lang = models.FloatField(null=True)
	block = models.CharField(max_length=50)
	blockRefernece = models.CharField(max_length=50)
