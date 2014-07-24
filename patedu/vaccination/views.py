# Create your views here.
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
from common.utils import get_a_Uuid, utcnow_aware
from datetime import datetime, timedelta
from models import VaccinationBeneficiary
from health_worker.models import HealthWorker
from random import randint

def APIInfo(request):
	return HttpResponse('Mobile Interface API')

def RestBeneficiary(request, id):
	try:
		vaccine_benef = VaccinationBeneficiary.objects.get(BeneficiaryId=id)
	except ObjectDoesNotExist:
		return HttpResponseBadRequest('Vaccination Beneficiary ID is not correct')

	if request.method == 'GET':
		return HttpResponse(json.dumps(vaccine_benef.json()), mimetype="application/json")
	elif request.method == 'PATCH' or request.method == 'PUT':
		req = json.loads(request.raw_post_data)
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
		return HttpResponse("Beneciary deleted")
	return HttpResponseBadRequest('Unknown http request type') 

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

		if name is not None and dob is not None:
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
			return HttpResponse( json.dumps(benef_post.json()), mimetype="application/json")
		else:
			return HttpResponseBadRequest('Name or DOB cannot be empty while adding a value')
	return HttpResponseBadRequest('Unsupported HTTP request type for this URL')