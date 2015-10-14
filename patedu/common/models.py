from django.db import models
from mcts_identities.models import Block, District, ANCBenef, IMMBenef

class AnalyticsData(models.Model):
	month = models.IntegerField()
	year = models.IntegerField()
	data = models.TextField()
	since_months = models.IntegerField()
	block = models.ForeignKey(Block)
	summary = models.TextField()
	summary_anc = models.TextField()
	summary_pnc = models.TextField()
	summary_imm = models.TextField()

class NHMTargets(models.Model):
	TARGET_TYPE_CHOICES = (
		('MREG', 'Mothers registrations'),
		('CREG', 'Children registrations'),
		('FIMM', 'Cull immunizations'),
		('FANC', 'Full ANC'),
		('DREP', 'Deliveries reported')
	)
	target_type = models.CharField(max_length=10, choices=TARGET_TYPE_CHOICES)
	target_year = models.IntegerField()
	target_value = models.IntegerField()
	last_updated = models.DateTimeField()
	district = models.ForeignKey(District)

class PopulationData(models.Model):
	population = models.IntegerField()
	last_updated = models.DateTimeField()
	MCTS_ID = models.CharField(max_length=30)
	unit_type = models.CharField(max_length=20)
	year = models.IntegerField(default=2015)

class ANCReportings(models.Model):
	benef = models.ForeignKey(ANCBenef, unique=True)
	anc1_date = models.DateField(null=True)
	anc2_date = models.DateField(null=True)
	anc3_date = models.DateField(null=True)
	anc4_date = models.DateField(null=True)
	delivery_date = models.DateField(null=True)

class IMMReportings(models.Model):
	benef = models.ForeignKey(IMMBenef, unique=True)
	measles_date = models.DateField(null=True)

class ExotelCallStatus(models.Model):
	sid = models.CharField(max_length=50, unique=True)
	subcenter = models.ForeignKey('mcts_identities.SubCenter', null=True)
	status = models.CharField(max_length=20)
	uid = models.IntegerField(null=True)
	role = models.CharField(max_length=10, null=True)
	mode = models.CharField(max_length=10, null=True)
	recording_url = models.TextField(null=True)
	date_initiated = models.DateField(null=True)
	dt_updated = models.DateTimeField()
	exotel_update_received = models.BooleanField(default=False)

class LOGUICL(models.Model):
	date = models.CharField(max_length=12)
	operator_name = models.CharField(max_length=50)
	benef_name =  models.CharField(max_length=50)
	address = models.TextField(null=True, blank=True)
	description = models.TextField()
	lmp_date = models.CharField(max_length=20)
	date_tt1 = models.CharField(max_length=20, null=True, blank=True)
	facility_current = models.CharField(max_length=50)	
	facility_past = models.CharField(max_length=50, null=True, blank=True)
	action = models.TextField()

	def json(self):
		return {
			'date':self.date,
			'operator_name':self.operator_name,
			'benef_name' : self.benef_name,
			'address': self.address,
			'description': self.description,
			'lmp_date': self.lmp_date,
			'date_tt1':self.date_tt1,
			'facility_current':self.facility_current,
			'facility_past':self.facility_past,
			'action':self.action
		}

	def populate(self, uicl_object):
		self.date = uicl_object.get("date")
		self.operator_name = uicl_object.get('operator_name')
		self.benef_name = uicl_object.get('benef_name')
		self.address = uicl_object.get('address')
		self.description = uicl_object.get('description')
		self.lmp_date = uicl_object.get('lmp_date')
		self.date_tt1 = uicl_object.get('date_tt1')
		self.facility_current = uicl_object.get('facility_current')
		self.facility_past = uicl_object.get('facility_past')
		self.action = uicl_object.get('action')
