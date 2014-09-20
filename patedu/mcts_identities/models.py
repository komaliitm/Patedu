from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
	value = models.CharField(max_length=256)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	village = models.CharField(max_length=100, null=True)
	village_mcts_id = models.CharField(max_length=100, null=True)

class HealthBlock(models.Model):
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

class HealthBlock(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)

class CareProvider(User):
	CP_DESIGNATIONS = (
		('ANM', 'ANM'),
		('DOC', 'Doctor'),
		('ADMIN', 'Management')
	)

	designation = models.CharField(choices=CP_DESIGNATIONS, max_length=20)
	phone = models.CharField(max_length=15, null=True)
	degree = models.CharField(max_length=20, null=True)
	address = models.ForeignKey(Address, null=True)

class CareGiver(User):
	CG_DESIGNATIONS = (
		('ASHA', 'asha worker'),
		('OTH', 'other persona')
	)

	designation = models.CharField(choices=CG_DESIGNATIONS, max_length=20)
	phone = models.CharField(max_length=15, null=True)
	education_status = models.CharField(max_length=20, null=True)
	address = models.ForeignKey(Address, null=True)
	reports_to = models.CharField(max_length=30, null=True)

class SubCenter(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	health_block = models.ForeignKey(HealthBlock)
	block = models.ForeignKey(Block)
	district = models.ForeignKey(District)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	caregiver = models.ForeignKey(CareGiver, null=True)
	careprovider = models.ForeignKey(CareProvider, null=True)


class Beneficiary(User):
	class NUMBER_TYPE():
		SELF = 0
		OTHER = 1
		ASHA = 2
		NBR = 3
	
	NUMBER_TYPE_CHOICES = (
		(NUMBER_TYPE.SELF, 'personal or family'),
		(NUMBER_TYPE.OTHER, 'others unknown'),
		(NUMBER_TYPE.ASHA, 'Asha workers number'),
		(NUMBER_TYPE.NBR, 'sombody in neighbourhood')
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
	active = models.BooleanField(default=True)
	MCTS_ID = models.CharField(max_length=100, null=True)
	notify_number = models.CharField(max_length=15)
	notify_number_type = models.IntegerField(choices=NUMBER_TYPE_CHOICES)
	gaurdian = models.CharField(max_length=50, null=True)
	gaurdian_relation = models.IntegerField(choices=RELATION_TYPE_CHOICES, null=True)
	language = models.IntegerField(choices=LANGUAGE_CHOICES, default=LANGUAGE.HINDI) 
	address = models.ForeignKey(Address, null=True)
	createdon = models.DateTimeField()
	modifiedon = models.DateTimeField()
	registration_year = models.CharField(max_length=20, null=True)


class ANCBenef(Beneficiary):
	LMP = models.DateField()
	EDD = models.DateField(null=True)
	husband = models.CharField(max_length=100)

class PNCBenef(Beneficiary):
	LMP = models.DateField()
	EDD = models.DateField()
	husband = models.CharField(max_length=100, null=True)
	ADD = models.DateField(null=True)
	delivery_place = models.CharField(max_length=20, null=True)
	delivery_type = models.CharField(max_length=20, null=True)
	complications = models.CharField(max_length=100, null=True)

class ImmunBenef(Beneficiary):
	dob = models.DateField()
	mother_name = models.CharField(max_length=100, null=True)
	mother_mcts_id = models.CharField(max_length=100, null=True) 







