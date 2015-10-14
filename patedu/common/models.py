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