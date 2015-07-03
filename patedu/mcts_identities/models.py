from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
	value = models.CharField(max_length=256)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	village = models.CharField(max_length=100, null=True)
	village_mcts_id = models.CharField(max_length=100, null=True)

class HealthFacility(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	head = models.CharField(max_length=50, null=True)

class Block(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	head = models.CharField(max_length=50, null=True)

class District(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	head = models.CharField(max_length=50, null=True)

class CareProvider(User):
	CP_DESIGNATIONS = (
		('ANM', 'ANM'),
		('DOC', 'Doctor'),
		('ADMIN', 'Management')
	)

	designation = models.CharField(choices=CP_DESIGNATIONS, max_length=20, default='ANM')
	phone = models.CharField(max_length=15, null=True)
	degree = models.CharField(max_length=20, null=True)
	address = models.ForeignKey(Address, null=True)

class CareGiver(User):
	CG_DESIGNATIONS = (
		('ASHA', 'asha worker'),
		('OTH', 'other persona')
	)

	designation = models.CharField(choices=CG_DESIGNATIONS, max_length=20, default='ASHA')
	phone = models.CharField(max_length=15, null=True)
	education_status = models.CharField(max_length=20, null=True)
	address = models.ForeignKey(Address, null=True)
	reports_to = models.CharField(max_length=30, null=True)

class SubCenter(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	health_facility = models.ForeignKey(HealthFacility)
	block = models.ForeignKey(Block)
	district = models.ForeignKey(District)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	

class Beneficiary(User):
	ANC = 'ANC'
	IMM = 'IMM'
	PNC = 'PNC'
	UNKNOWN = 'UNKNOWN'

	class NUMBER_TYPE():
		SELF = 0
		OTHER = 1
		ASHA = 2
		NBR = 3
		RTL = 4
	
	NUMBER_TYPE_MAP = {
		'self':0,
		'other':1,
		'asha':2,
		'neighbour':3,
		'relative':4,
	}

	NUMBER_TYPE_REVERSE_MAP = {
		'0':'self',
		'1':'other',
		'2':'asha',
		'3':'neighbour',
		'4':'relative'
	}

	NUMBER_TYPE_CHOICES = (
		(NUMBER_TYPE.SELF, 'personal or family'),
		(NUMBER_TYPE.OTHER, 'others unknown'),
		(NUMBER_TYPE.ASHA, 'Asha workers number'),
		(NUMBER_TYPE.NBR, 'sombody in neighbourhood'),
		(NUMBER_TYPE.RTL, 'sombody in relation')
	)

	class RELATION_TYPE():
		FATHER = 1
		MOTHER = 2
		FAMILY = 3
		OTHER = 4
	
	RELATION_TYPE_CHOICES = (
		(RELATION_TYPE.FATHER, 'father'),
		(RELATION_TYPE.MOTHER, 'mother'),
		(RELATION_TYPE.FAMILY, 'someone in family'),
		(RELATION_TYPE.OTHER, 'other/undefined')
	)

	class LANGUAGE():
		HINDI = 1
		ENGLISH = 2 
		TELUGU = 3

	LANGUAGE_CHOICES = (
		(LANGUAGE.HINDI, 'Hindi'),
		(LANGUAGE.ENGLISH, 'English'),
		(LANGUAGE.TELUGU, 'Telugu')
	)

	def get_type(self):
		if hasattr(self, 'ancbenef'):
			return self.ANC
		elif hasattr(self, 'immbenef'):
			return self.IMM
		elif hasattr(self, 'pncbenef'):
			return self.PNC
		else:
			return self.UNKNOWN
		

	active = models.BooleanField(default=True)
	MCTS_ID = models.CharField(max_length=100, null=True)
	notify_number = models.CharField(max_length=15, null=True)
	notify_number_type = models.IntegerField(choices=NUMBER_TYPE_CHOICES, null=True)
	gaurdian = models.CharField(max_length=50, null=True)
	gaurdian_relation = models.IntegerField(choices=RELATION_TYPE_CHOICES, null=True)
	language = models.IntegerField(choices=LANGUAGE_CHOICES, default=LANGUAGE.HINDI) 
	address = models.ForeignKey(Address, null=True, related_name='beneficiaries')
	createdon = models.DateTimeField()
	modifiedon = models.DateTimeField()
	subcenter = models.ForeignKey(SubCenter)
	registration_year = models.CharField(max_length=20, null=True)
	caregiver = models.ForeignKey(CareGiver, null=True)
	careprovider = models.ForeignKey(CareProvider, null=True, related_name="beneficiaries")

class ANCBenef(Beneficiary):
	ANC_SPAN = 270

	LMP = models.DateField()
	EDD = models.DateField(null=True)
	husband = models.CharField(max_length=100)

class PNCBenef(Beneficiary):
	PNC_SPAN = 90
	LMP = models.DateField(null=True)
	EDD = models.DateField(null=True)
	husband = models.CharField(max_length=100, null=True)
	ADD = models.DateField(null=True)
	delivery_place = models.CharField(max_length=20, null=True)
	delivery_type = models.CharField(max_length=20, null=True)
	complications = models.CharField(max_length=100, null=True)

class IMMBenef(Beneficiary):
	IMM_SPAN = 730
	dob = models.DateField(null=True)
	child_name = models.CharField(max_length=100, null=True)
	child_sex = models.CharField(max_length=10, null=True)
	mother_name = models.CharField(max_length=100, null=True)
	mother_mcts_id = models.CharField(max_length=100, null=True) 







