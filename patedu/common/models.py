from django.db import models
from mcts_identities.models import Block

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