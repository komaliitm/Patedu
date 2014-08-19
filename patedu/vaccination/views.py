# Create your views here.
from __future__ import absolute_import
import json
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import RequestContext
from django.contrib.auth.models import User
from django.conf import settings
from common.utils import pprint, utcnow_aware
import time
from django.http import HttpResponseNotAllowed
import dateutil.parser
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from common.utils import get_a_Uuid, utcnow_aware, toHex
from datetime import datetime, timedelta
from vaccination.models import *
from health_worker.models import HealthWorker
from random import randint
import pytz
from celery import shared_task
import unicodedata
from sms.views import *
import binascii
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import sys

@csrf_exempt
def APIInfo(request):
	return HttpResponse('Mobile Interface API')

@csrf_exempt
def RestBeneficiary(request, id):
	try:
		vaccine_benef = VaccinationBeneficiary.objects.get(BeneficiaryId=id)
	except ObjectDoesNotExist:
		return HttpResponseBadRequest('Vaccination Beneficiary ID is not correct')

	if request.method == 'GET':
		return HttpResponse(json.dumps(vaccine_benef.json()), mimetype="application/json")
	elif request.method == 'POST':
		req = request.POST
		name = req.get('name')
		notif_num = req.get('notif_num')
		dob = req.get('dob')
		sex = req.get('sex')
		gaurdian_name = req.get('gaurdian_name')
		language = req.get('language')
		hw_num = req.get('hw_num')
		is_verified = req.get('is_verified')
		
		if name is not None: vaccine_benef.ChildName = name
		if dob is not None:
			dob = dateutil.parser.parse(dob).date()
			vaccine_benef.Dob = dob
		if notif_num is not None: vaccine_benef.NotifyNumber = notif_num
		if sex is not None: vaccine_benef.Sex = sex
		if gaurdian_name is not None: vaccine_benef.Gaurdian_name = gaurdian_name
		if language is not None: vaccine_benef.Language = language
		if is_verified is not None: vaccine_benef.isVerified = is_verified

		if hw_num is not None:
			hw = None
			try:
				hw = HealthWorker.objects.get(phone=hw_num)
			except ObjectDoesNotExist:
				hw = HealthWorker(phone=hw_num, username=hw_num, password= "hw123")
				hw.save()
			vaccine_benef.health_worker = hw
		
		vaccine_benef.ModifiedOn = utcnow_aware()

		vaccine_benef.save()
		return HttpResponse( json.dumps(vaccine_benef.json()), mimetype="application/json")
	elif request.method == 'DELETE':
		vaccine_benef.delete()
		return HttpResponse("Beneficiary deleted")
	return HttpResponseBadRequest('Unknown http request type') 

@csrf_exempt
def RestBeneficiaryList(request):
	if request.method == 'GET':
		name = request.GET.get('name')
		notif_num = request.GET.get('notif_num')
		dob = request.GET.get('dob')
		sex = request.GET.get('sex')
		gaurdian_name = request.GET.get('gaurdian_name')
		language = request.GET.get('language')
		hw_num = request.GET.get('hw_num')
		is_verified = request.GET.get('is_verified')

		filter_set ={}

		if name is not None: filter_set['ChildName'] = name
		if dob is not None:
			dob = dateutil.parser.parse(dob).date()
			filter_set['Dob'] = dob
		if notif_num is not None: filter_set['NotifyNumber'] = notif_num
		if sex is not None: filter_set['Sex'] = sex
		if gaurdian_name is not None: filter_set['Gaurdian_name']= gaurdian_name
		if language is not None: filter_set['Language'] = language
		if is_verified is not None: filter_set['isVerified'] = is_verified 

		if hw_num is not None:
			hw = None
			try:
				hw = HealthWorker.objects.get(phone=hw_num)
			except ObjectDoesNotExist:
				hw = HealthWorker(phone=hw_num, username=hw_num, password= "hw123")
				hw.save()
			filter_set['health_worker'] = hw
		
		beneficiaries = VaccinationBeneficiary.objects.all()
		for k, v in filter_set.items():
			if v:
				beneficiaries = beneficiaries.filter(**{k: v})

		ret_val = [record.json() for record in beneficiaries]
		return HttpResponse(json.dumps(ret_val), mimetype="application/json")
	elif request.method == 'POST':
		name = request.POST.get('name')
		notif_num = request.POST.get('notif_num')
		dob = request.POST.get('dob')
		sex = request.POST.get('sex')
		gaurdian_name = request.POST.get('gaurdian_name')
		language = request.POST.get('language')
		hw_num = request.POST.get('hw_num')

		if name is not None and dob is not None and notif_num is not None:
			dob = dateutil.parser.parse(dob).date()
			benef_post = VaccinationBeneficiary(ChildName=name, Dob=dob)
			if notif_num is not None: benef_post.NotifyNumber = notif_num
			if sex is not None: benef_post.Sex = sex
			if gaurdian_name is not None: benef_post.Gaurdian_name = gaurdian_name
			if language is not None: benef_post.Language = language
			
			if hw_num is not None:
				hw = None
				try:
					hw = HealthWorker.objects.get(phone=hw_num)
				except ObjectDoesNotExist:
					hw = HealthWorker(phone=hw_num, username=hw_num, password= "hw123")
					hw.save()
				benef_post.health_worker = hw
			benef_post.isVerified = False
			benef_post.VerificationCode = randint(1000, 9999)
			benef_post.CreatedOn = utcnow_aware()
			benef_post.ModifiedOn = utcnow_aware()
			benef_post.BeneficiaryId = get_a_Uuid()

			benef_post.save()
			platform = sys.platform
			print 'platform'
			generate_schedule(benef_post.BeneficiaryId)
			welcome_msg_id = 'VAC_WELCOME'
			if platform == 'linux2':
				result = send_welcome_msg.delay(benef_post.BeneficiaryId, welcome_msg_id)
			else:
				result = send_welcome_msg(benef_post.BeneficiaryId, welcome_msg_id)
			return HttpResponse( json.dumps(benef_post.json()), mimetype="application/json")
		else:
			return HttpResponseBadRequest('Name or DOB cannot be empty while adding a value')
	return HttpResponseBadRequest('Unsupported HTTP request type for this URL')

@shared_task
def send_welcome_msg(benef_id, msg_id):
	ret = {"status":0,
	"msg":""}

	try:
		vaccine_benef = VaccinationBeneficiary.objects.get(BeneficiaryId=benef_id)
	except ObjectDoesNotExist:
		ret["status"] = 1
		ret["msg"] = "Vaccination Beneficiary ID is not correct"
		return ret

	sms_msg = ''
	try:
		sms_msg = SMSMessages.objects.get(msg_identifier=msg_id).msg
	except ObjectDoesNotExist:
		print 'ERROR: SMS msg not found for the id: '+msg_id
		ret["status"] = 1
		ret["msg"] = "Welcome message for given ID does not exist: "+msg_id
		return ret

	sms_msg_hexlified = toHex(sms_msg)
	benef_number = vaccine_benef.NotifyNumber
	#send sms
	pprint('sending welcome sms')
	sent_code = SendSMSUnicode(recNum=benef_number, msgtxt=sms_msg_hexlified)

	if 'Status=1' in sent_code:
		ret["status"] = 1
		ret["msg"] = sent_code
		return ret
	elif 'Status=0' in sent_code:
		ret["status"] = 0
		ret["msg"] = "Welcome message successfully sent"


def generate_schedule(benef_id):
	ret = {"status":0,
	"msg":""}

	try:
		vaccine_benef = VaccinationBeneficiary.objects.get(BeneficiaryId=benef_id)
	except ObjectDoesNotExist:
		ret["status"] = 1
		ret["msg"] = "Vaccination Beneficiary ID is not correct"
		return ret

	if vaccine_benef.isScheduleGenerated:
		ret["status"] = 1
		ret["msg"] = "for given beneficiary the schedule is already generated"
		return ret

	#Generate schedule here
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz).date()

	dob = vaccine_benef.Dob
	delta_dob = today - dob
	today_weeks = delta_dob.days/7

	#TODO: Accomodate richness in model itself
	richness = [
		{'stage':'1M', 'days':30},
		{'stage':'1W', 'days':7},
		{'stage':'1D', 'days':1},
		{'stage':'AW1', 'days':15},
		{'stage':'AW2', 'days':4}
	]

	#find all vaccines greater than today_weeks
	vaccines = Vaccinations.objects.filter(AgeInWeeks__gte=today_weeks)
	for vaccine in vaccines:
		vaccine_eta = dob + timedelta(days=vaccine.AgeInWeeks*7)
		
		#Generate the reminders for future based on richness level
		for level in richness:
			rem_eta = vaccine_eta - timedelta(days=level['days'])
			if rem_eta >= today:
				try:
					rem_template = VaccineReminderTemplate.objects.get(Vaccine=vaccine, stage=level['stage'], Language=vaccine_benef.Language)
					vac_rem = VaccineReminder(vaccine_reference=rem_template, vaccination_beneficiary= vaccine_benef, dueDate= rem_eta, vaccDate=vaccine_eta)
					vac_rem.save()
				except ObjectDoesNotExist:
					print 'Error: Template missing for the vaccine: '+vaccine.vaccineId+' '+level['stage']+' '+vaccine_benef.Language
			else:
				#TODO: Account for recently missed vaccinations
				continue

@shared_task
def send_reminders():
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)
	pprint('Executing send_reminders scheduled function')
	today_date = today.date()

	reminders = VaccineReminder.objects.filter( Q(state=2)|Q(state=1), Q(dueDate=today_date))

	for reminder in reminders:
		language = reminder.vaccine_reference.Language
		vaccine_name = reminder.vaccine_reference.Vaccine.VaccineName
		benef_name = reminder.vaccination_beneficiary.ChildName
		benef_number = reminder.vaccination_beneficiary.NotifyNumber
		gaurdian_name = reminder.vaccination_beneficiary.Gaurdian_name
		hw = reminder.vaccination_beneficiary.health_worker
		if hw and hw.first_name:
			hw_name = hw.first_name+' '+hw.last_name
		else:
			hw_name = ''
		vacc_date = '{0.month}/{0.day}/{0.year}'.format(reminder.vaccDate)

		#TODO: Accomodate for IVR, and email later
		sms_id = reminder.vaccine_reference.sms_message
		sms_temp = ''
		try:
			sms_temp = SMSMessages.objects.get(msg_identifier=sms_id).msg
		except ObjectDoesNotExist:
			print 'ERROR: SMS msg not found for the id: '+sms_id
			continue
		sms_temp = sms_temp.replace(u'childName', unicode(benef_name))
		sms_temp = sms_temp.replace(u'vaccineName', unicode(vaccine_name))
		sms_temp = sms_temp.replace(u'date', unicode(vacc_date))
		sms_temp = sms_temp.replace(u'hwName', unicode(hw_name))
		sms_msg = sms_temp
		#sms_msg_hexlified = binascii.hexlify(sms_msg.encode('utf-8'))
		sms_msg_hexlified = toHex(sms_msg)
		#send sms
		print 'sending sms'
		sent_code = SendSMSUnicode(recNum=benef_number, msgtxt=sms_msg_hexlified)

		if 'Status=1' in sent_code:
			reminder.state = 1
			reminder.errorCode = sent_code
			reminder.save()
		elif 'Status=0' in sent_code:
			reminder.state = 0
			reminder.save()
		break


@shared_task
def sms_registrations():
	incoming_msgs = ReceiveSMSToday()


		


