from django.db import models
from mcts_identities.models import *

class Events(models.Model):
	ANC_REG_VAL = 'anc_reg'
	PNC_REG_VAL = 'pnc_reg'
	IMM_REG_VAL = 'imm_reg'
	class CATEGORY():
			VACC = 1
			CHILD_VACC = 13
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
		(CATEGORY.CHILD_VACC, 'any kind of vaccination given to child'),
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
	content_index = models.CharField(max_length=20, null=True)
	category = models.IntegerField(choices=CATEGORY_CHOICES, null=True)

class Transactions(models.Model):
	beneficiary = models.ForeignKey(Beneficiary)
	timestamp = models.DateTimeField()
	event = models.ForeignKey(Events)
	subcenter = models.ForeignKey(SubCenter)
	notes = models.CharField(max_length=256, null=True)

class DueEvents(models.Model):
	UNHANDLED = 0
	SCH = 1
	AW = 2
	SCHAW =3

	HANDLED_LEVELS = (
		(UNHANDLED, 'unhandled'),
		(SCH, 'schedule message sent'),
		(AW, 'awareness message sent'),
		(SCHAW, 'both awareness and schedule message sent')
	)

	beneficiary = models.ForeignKey(Beneficiary)
	date = models.DateField()
	event = models.ForeignKey(Events)
	subcenter = models.ForeignKey(SubCenter)
	notes = models.CharField(max_length=256, null=True)
	handled = models.IntegerField(choices=HANDLED_LEVELS, default=UNHANDLED)

class OverDueEvents(models.Model):
	beneficiary = models.ForeignKey(Beneficiary)
	date = models.DateField()
	event = models.ForeignKey(Events)
	subcenter = models.ForeignKey(SubCenter)
	notes = models.CharField(max_length=256)
	
class Content(models.Model):
	# SMS = 0
	# EMAIL =1
	# IVR =2

	# MEDIUM_CATEGORY = (
	# 	(SMS, "sms"),
	# 	(EMAIL, "email"),
	# 	(IVR, "ivr")
	# )

	class LANGUAGE():
		HINDI = 1
		ENGLISH = 2 
		TELUGU = 3

	LANGUAGE_CHOICES = (
		(LANGUAGE.HINDI, 'Hindi'),
		(LANGUAGE.ENGLISH, 'English'),
		(LANGUAGE.TELUGU, 'Telugu')
	)

	sch_msg_sms = models.CharField(max_length=512)
	sch_msg_email = models.CharField(max_length=2048, null=True)
	sch_msg_ivr = models.CharField(max_length=2048, null=True)
	
	aw_msg_sms = models.CharField(max_length=512)
	aw_msg_email = models.CharField(max_length=2048, null=True)
	aw_msg_ivr = models.CharField(max_length=2048, null=True)

	language = models.IntegerField(choices=LANGUAGE_CHOICES, default=LANGUAGE.HINDI)
	msg_index = models.CharField(max_length=20)

class ContentDelivered(models.Model):
	SMS = 0
	EMAIL =1
	IVR =2

	MEDIUM_CATEGORY = (
		(SMS, "sms"),
		(EMAIL, "email"),
		(IVR, "ivr")
	)

	SUCCESS = 0
	ISSUE = 1
	FAILURE = 2


	DELIVERY_STATUS = (
		(SUCCESS, "delivery is successful"),
		(ISSUE, "delivery is not successful but has  to be retried")
		(FAILURE, "delivery is failed permanently")
	)

	msg = models.CharField(max_length=2048)
	medium = models.IntegerField(choices=MEDIUM_CATEGORY, default=SMS)
	timestamp = models.DateTimeField()
	status = models.IntegerField(choices=DELIVERY_STATUS)
	benefeciary = models.ForeignKey(Beneficiary)
