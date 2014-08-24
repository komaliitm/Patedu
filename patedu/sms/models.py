from django.db import models
from vaccination.models import SMSMessages

class IncomingSMS(models.Model):
	sender_num = models.CharField(max_length=20)
	dtime = models.DateTimeField(null=True)
	msgtxt = models.CharField(max_length=1024)
	processed = models.BooleanField(default=False)
	remark = models.CharField(max_length=1024)

class LastRetrieveTime(models.Model):
	state_options = ( (0, "success"),
                (1, "failure") )
	last_ret = models.DateTimeField()
	status = models.IntegerField(choices=state_options)