from django.db import models
from django.contrib.auth.models import User
from isodate import datetime_isoformat

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

	def json(self):
		json_dict = {
			'MCTS_ID': self.MCTS_ID,
			'name': self.name,
			'head': self.head
		}
		return json_dict

class Block(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	head = models.CharField(max_length=50, null=True)

	def json(self):
		json_dict = {
			'MCTS_ID': self.MCTS_ID,
			'name': self.name,
			'head': self.head			
		}
		return json_dict

class District(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	head = models.CharField(max_length=50, null=True)

	def json(self):
		json_dict = {
			'MCTS_ID': self.MCTS_ID,
			'name': self.name,
			'head': self.head
		}
		return json_dict

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

	def json(self):
		json_dict = {
			'designation':self.designation,
			'phone':self.phone,
			'degree':self.degree,
			'village':self.address.village if self.address else None,
			'village_mcts_id':self.address.village_mcts_id if self.address else None,
			'name':self.first_name+' '+self.last_name
		}
		return json_dict

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

	def json(self):
		json_dict = {
			'designation':self.designation,
			'phone':self.phone,
			'education_status':self.education_status,
			'village':self.address.village if self.address else None,
			'village_mcts_id':self.address.village_mcts_id if self.address else None,
			'name':self.first_name+' '+self.last_name,
			'reports_to':self.reports_to
		}
		return json_dict

class SubCenter(models.Model):
	MCTS_ID = models.CharField(max_length=50, null=True)
	health_facility = models.ForeignKey(HealthFacility)
	block = models.ForeignKey(Block, related_name='subcenters')
	district = models.ForeignKey(District)
	_lat = models.FloatField(null=True)
	_long = models.FloatField(null=True)
	name = models.CharField(max_length=50)
	
	def json(self):
		json_dict = {
			'MCTS_ID':self.MCTS_ID,
			'health_facility':self.health_facility.json(),
			'block':self.block.json(),
			'district':self.district.json(),
			'name':self.name
		}
		return json_dict

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
			return self.UNKNOW		
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
	caregiver = models.ForeignKey(CareGiver, null=True, related_name="beneficiaries")
	careprovider = models.ForeignKey(CareProvider, null=True, related_name="beneficiaries")

	def base_json(self, date_then):
		json_dict = {}
		json_dict['name'] = self.first_name+' '+self.last_name
		json_dict['active'] = self.active
		json_dict['MCTS_ID'] = self.MCTS_ID
		json_dict['notify_number'] = self.notify_number
		json_dict['notify_number_type'] = self.notify_number_type
		json_dict['gaurdian'] = self.gaurdian
		json_dict['language'] = self.language
		json_dict['village'] = self.address.village if self.address else None
		json_dict['village_mcts_id'] = self.address.village_mcts_id if self.address else None
		json_dict['createdon'] = datetime_isoformat(self.createdon) if self.createdon else None
		json_dict['modifiedon'] = datetime_isoformat(self.modifiedon) if self.modifiedon else None
		json_dict['subcenter'] = self.subcenter.json()
		json_dict['registration_year'] = self.registration_year
		json_dict['caregiver'] = self.caregiver.json() if self.caregiver else None
		json_dict['careprovider'] = self.careprovider.json() if self.careprovider else None
		json_dict['odue_events'] = [od_event.json() for od_event in self.odue_events.filter(date__gte=date_then)]
		json_dict['due_events'] = [d_event.json() for d_event in self.due_events.filter(date__gte=date_then)]
		json_dict['txns'] = [txn.json() for txn in self.txns.all()]

		return json_dict

class ANCBenef(Beneficiary):
	TYPE = 'ANC'
	ANC_SPAN = 270
	LMP = models.DateField()
	EDD = models.DateField(null=True)
	husband = models.CharField(max_length=100)

	def json(self, date_then):
		dict = self.base_json(date_then)
		dict['LMP'] = self.LMP.isoformat() if self.LMP else None
		dict['EDD'] = self.EDD.isoformat() if self.EDD else None
		dict['husband'] = self.husband
		return dict

class PNCBenef(Beneficiary):
	TYPE = 'PNC'
	PNC_SPAN = 90
	LMP = models.DateField(null=True)
	EDD = models.DateField(null=True)
	husband = models.CharField(max_length=100, null=True)
	ADD = models.DateField(null=True)
	delivery_place = models.CharField(max_length=20, null=True)
	delivery_type = models.CharField(max_length=20, null=True)
	complications = models.CharField(max_length=100, null=True)

	def json(self, date_then):
		dict = self.base_json(date_then)
		dict['LMP'] = self.LMP.isoformat() if self.LMP else None
		dict['EDD'] = self.EDD.isoformat() if self.EDD else None
		dict['husband'] = self.husband
		dict['ADD'] = self.ADD.isoformat()
		dict['delivery_place'] = self.delivery_place
		dict['delivery_type'] = self.delivery_type
		dict['complications'] = self.complications
		return dict

class IMMBenef(Beneficiary):
	TYPE = 'IMMUNIZATION'
	IMM_SPAN = 730
	dob = models.DateField(null=True)
	child_name = models.CharField(max_length=100, null=True)
	child_sex = models.CharField(max_length=10, null=True)
	mother_name = models.CharField(max_length=100, null=True)
	mother_mcts_id = models.CharField(max_length=100, null=True) 

	def json(self, date_then):
		dict = self.base_json(date_then)
		dict['dob'] = self.dob.isoformat()
		dict['child_name'] = self.child_name
		dict['child_sex'] = self.child_sex
		dict['mother_name'] = self.mother_name
		dict['mother_mcts_id'] = self.mother_mcts_id
		return dict




