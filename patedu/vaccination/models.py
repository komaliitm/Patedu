from django.db import models
from health_worker.models import HealthWorker
from isodate import datetime_isoformat

class Vaccinations(models.Model):
	vaccineId = models.CharField(max_length=50, primary_key=True)
	VaccineName = models.CharField(max_length=50)
	AgeInWeeks = models.IntegerField()
	notes = models.CharField(max_length=64)

class VaccinationBeneficiary(models.Model):
	lang_choices = ( ('HIN', 'hindi'),
					('ENG', 'English')	
		)
	BeneficiaryId = models.CharField(max_length=30, primary_key=True)
	ChildName = models.CharField(max_length=256)
	Sex = models.CharField(max_length=50)
	NotifyNumber = models.CharField(max_length=50, null=False)
	VerificationCode = models.IntegerField(max_length=50)
	Dob = models.DateField(null=False)
	isVerified = models.BooleanField()
	isScheduleGenerated = models.BooleanField(default=False) 
	health_worker = models.ForeignKey(HealthWorker, null=True)
	Gaurdian_name = models.CharField(max_length=256)
	Language = models.CharField(choices=lang_choices, max_length=16, default='HIN')
	CreatedOn = models.DateTimeField()
	ModifiedOn = models.DateTimeField()
	def json(self):
		hw_phone = None
		if self.health_worker is not None:
			hw_phone = self.health_worker.phone
		return {
			'Id': self.BeneficiaryId,
			'name' : self.ChildName,
			'sex' : self.Sex,
			'notify_number' : self.NotifyNumber,
			'reg_code' :  self.VerificationCode,
			'dob' : self.Dob.isoformat(),
			'is_verified' : self.isVerified,
			'health_worker_phone':hw_phone,
			'lang': self.Language,
			'gaurdian_name': self.Gaurdian_name,
			'ModifiedOn': datetime_isoformat(self.ModifiedOn),
		}

	def __unicode__(self):
		return self.ChildName+"_"+self.Sex+"_"+self.NotifyNumber


class VaccineReminderTemplate(models.Model):
	stage_options = ( ("1M", 'one month'),
				("1W", 'one week'),
				("1D", 'one day'),
				("AW1", 'awareness 1'),
				("AW2", 'awareness 2'), 
		 )
	lang_choices = ( ('HIN', 'hindi'),
					('ENG', 'English')	
		)
	Vaccine = models.ForeignKey(Vaccinations)
	stage = models.CharField(choices=stage_options, max_length=3)
	Language = models.CharField(choices=lang_choices, max_length=16)
	sms_message = models.CharField(max_length=64, null=True)
	ivr_message = models.CharField(max_length=64, null=True)
	email_message =  models.CharField(max_length=64, null=True)

	def __unicode__(self):
		return self.Vaccine.VaccineName

class SMSMessages(models.Model):
	msg_identifier = models.CharField(max_length=64, primary_key=True)
	msg = models.CharField(max_length=640)

class VaccineReminder(models.Model):
	state_options = ( (0, "sent"),
                (1, "sent but failed"),
                (2, "not sent") )
	
	vaccine_reference = models.ForeignKey(VaccineReminderTemplate)
	vaccination_beneficiary = models.ForeignKey(VaccinationBeneficiary)
	state = models.IntegerField(choices=state_options, default=2)
	errorCode = models.CharField(max_length=1024, null=True)
	dueDate = models.DateField()
	vaccDate= models.DateField()