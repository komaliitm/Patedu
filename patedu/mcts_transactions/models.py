from django.db import models
from mcts_identities.models import *

class Events(models.Model):
	class CATEGORY():
			VACC = 1
			CHILD_REG = 2 
			DELIVERY = 3
			ANC = 4
			INF_MORT = 5
			CHILD_MORT = 6
			PNC_COMPLICATION = 7
			ANC_COMPLICATION = 8
			NC_COMPLICATION = 9
			MAT_MORTALITY = 10
			SUPLEMENTS = 11
			MOTHER_REG = 12

	CATEGORY_CHOICES = (
		(CATEGORY.VACC, 'any kind of vaccination given'),
		(CATEGORY.CHILD_REG, 'child registration'),
		(CATEGORY.DELIVERY, 'delivery'),
		(CATEGORY.ANC, 'ANC during pregnancy'),
		(CATEGORY.INF_MORT, 'infant mortalities reported'),
		(CATEGORY.CHILD_MORT, 'child mortality reported'),
		(CATEGORY.PNC_COMPLICATION, 'pnc complication'),
		(CATEGORY.ANC_COMPLICATION, 'anc complication'),
		(CATEGORY.NC_COMPLICATION, 'nc complication'),
		(CATEGORY.MAT_MORTALITY, 'maternal mortality'),
		(CATEGORY.SUPLEMENTS, 'supplements'),
		(CATEGORY.MOTHER_REG, 'mother registration')
	)

	MCTS_ID = models.CharField(max_length=50)
	val = models.CharField(max_length=50)
	content_index = models.CharField(max_length=20)
	category = models.IntegerField(choices=CATEGORY_CHOICES)

class Transactions(models.Model):
	beneficiary = models.ForeignKey(Beneficiary)
	timestamp = models.DateTimeField()
	event = models.ForeignKey(Events)
	subcenter = models.ForeignKey(SubCenter)
	notes = models.CharField(max_length=256)

class DueEvents(models.Model):
	beneficiary = models.ForeignKey(Beneficiary)
	date = models.DateField()
	event = models.ForeignKey(Events)
	subcenter = models.ForeignKey(SubCenter)
	notes = models.CharField(max_length=256)
