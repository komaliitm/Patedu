from django.db import models
from vaccination.models import SMSMessages

class IncomingSMS(models.Model):
	sender_num = models.CharField(max_length=20)
	dtime = models.DateTimeField(null=True)
	msgtxt = models.CharField(max_length=1024)
	processed = models.BooleanField(default=False)
	remark = models.CharField(max_length=1024)