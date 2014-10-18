# -*- coding: utf-8 -*-

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
from random import randint
import pytz
from celery import shared_task
import unicodedata
from sms.sender import SendSMSUnicode
import binascii
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import sys
from mcts_transactions.models import *
from mcts_identities.models import *
from sms.sender import SendSMSUnicode
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render
from math import ceil

class StaticData:
	SCHEDULE_MSG =0
	AWARENESS_MSG = 1
	SENDER = 0
	CLEANER = 1
	REACHONLYSELF = 0

def SendSchSMS(role=StaticData.SCHEDULE_MSG, job=StaticData.SENDER, reach = StaticData.REACHONLYSELF):
	#TODO pick timezone from DB
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	now_utc = utcnow_aware()
	now = now_utc.astimezone(tz)
	month = now.month
	year = now.year

	# #Find all due and unhandled services this month.
	_allDueCurrentMonth = DueEvents.objects.filter(date__year = year, date__month = month)

	#if category == StaticData.SCHEDULE_MSG:
	sms_template = u"<prelude> <name> की <event> <category> इस महीने होनी अति आवश्यक है. कृपया अविलंब अपनी आशा बहनजी <asha_name> से संपर्क करे. धन्यवाद!"

	# #for each due service send an Message
	for _dueService in _allDueCurrentMonth:
		benef = _dueService.beneficiary
		if benef.notify_number_type != Beneficiary.NUMBER_TYPE.SELF: 
			continue
		benef_number = benef.notify_number
		if benef.ancbenef:
			prelude = u"श्रीमती"
			category = u"जाँच/टीकाकरण"
		elif benef.immbenef:
			prelude = u"बच्चे"
			category = u"टीकाकरण"

		name = unicode(benef.first_name)
		event = unicode(_dueService.event.val)
		asha_name = u''
		if benef.caregiver:
			asha_name = unicode(benef.caregiver.first_name) 

		sms_text = sms_template.replace(u"<prelude>", prelude).replace(u"<name>", name).replace(u"<category>", category).replace(u"<event>", event).replace(u"<asha_name>", asha_name)
		print sms_text
		sms_msg_hexlified = toHex(sms_text)
		#send sms
		print 'sending sms'
		
		#sent_code = SendSMSUnicode(recNum=benef_number, msgtxt=sms_msg_hexlified)

		if 'Status=1' in sent_code:
			ContentDelivered.objects.create(msg= sms_text, medium=ContentDelivered.SMS, timestamp = utcnow_aware(), status=1, beneficiary = benef)
		elif 'Status=0' in sent_code:
			ContentDelivered.objects.create(msg= sms_text, medium=ContentDelivered.SMS, timestamp = utcnow_aware(), status=0, beneficiary = benef)


def DashboardPage(request):
	_allBlocks = Block.objects.all()
	blocks = [block for block in _allBlocks]
	return render(request, "dasboard_subcenteratblock.html", {'blocks':blocks})

def ProcessSubcenterData(benefs, sub, since_months, reg_type):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)

	Overdue = 0
	new_reg = 0
	GivenServices = 0
	OverDueRate = 0
	if benefs:
		txs_service = Transactions.objects.filter(subcenter=sub, beneficiary__in = benefs, timestamp__gte=since_months).exclude(event__val=reg_type)
		txs_reg = Transactions.objects.filter(subcenter=sub, event__val=reg_type, timestamp__gte=since_months)
		dues_service = DueEvents.objects.filter(subcenter=sub, beneficiary__in = benefs, date__gte=since_months.date())

		GivenServices = txs_service.count()

		overdues_service = OverDueEvents.objects.filter(subcenter=sub, beneficiary__in = benefs, date__gte=since_months.date())
		Overdue = overdues_service.count()
		new_reg = txs_reg.count()
		
		if Overdue > 0:
			last_overdue = overdues_service.order_by('date')[0]
			delta_months = ceil(float((today_utc.date() - last_overdue.date).days)/30)
			OverDueRate = float(Overdue)/delta_months

		if dues_service:
			Adherence = txs_service.count() * 100 / dues_service.count()
		else:
			Adherence = None
		
	else:
		Adherence = None

	return {
			'Overdue':Overdue,
			'new_reg':new_reg,
			'GivenServices':GivenServices,
			'OverDueRate':OverDueRate,
			'Adherence':Adherence
	}

def DashboardData(request, blockid = None):
	if blockid:
		blocks = Block.objects.filter(id=blockid)
		if blocks.count() == 0:
			return HttpResponseBadRequest('wrong block id provided in the request')
		blockname = blocks[0].name
	else:
		blocks = Block.objects.all()
		blockname = 'All'

	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)

	#process GET params
	since_months = int(request.GET.get('since_months')) if request.GET.get('since_months') else None
	if since_months:
		since_months = today_utc - timedelta(days=since_months*30)
	else:
		since_months = today_utc - timedelta(days=360)

	data = []
	summary = {}
	num_good = 0
	num_poor = 0
	num_avg = 0
	for block in blocks:
		#find all the subcenters in the block
		subs = SubCenter.objects.filter(block=block)
		for sub in subs:
			sub_data = {}

			#total beneficiaries.
			anc_benefs = ANCBenef.objects.filter(subcenter = sub)
			pnc_benefs = PNCBenef.objects.filter(subcenter = sub)
			imm_benefs = IMMBenef.objects.filter(subcenter = sub)

			sub_data["Beneficiaries_anc"] = anc_benefs.count()
			sub_data["Beneficiaries_pnc"] = pnc_benefs.count()
			sub_data["Beneficiaries_imm"] = imm_benefs.count()

			data_anc = ProcessSubcenterData(anc_benefs, sub, since_months, Events.ANC_REG_VAL)
			data_pnc = ProcessSubcenterData(pnc_benefs, sub, since_months, Events.PNC_REG_VAL)
			data_imm = ProcessSubcenterData(imm_benefs, sub, since_months, Events.IMM_REG_VAL)

			sub_data["Beneficiaries_anc"] = anc_benefs.count()
			sub_data["Beneficiaries_pnc"] = pnc_benefs.count()
			sub_data["Beneficiaries_imm"] = imm_benefs.count()
			sub_data["Adherence_anc"] = data_anc["Adherence"]
			sub_data["Adherence_pnc"] = data_pnc["Adherence"]
			sub_data["Adherence_imm"] = data_imm["Adherence"]
			sub_data["new_reg_anc"] = data_anc["new_reg"]
			sub_data["new_reg_pnc"] = data_pnc["new_reg"]
			sub_data["new_reg_imm"] = data_imm["new_reg"]
 			sub_data["Overdue_anc"] = data_anc["Overdue"]
			sub_data["Overdue_pnc"] = data_pnc["Overdue"]
			sub_data["Overdue_imm"] = data_imm["Overdue"]
			sub_data["GivenServices_anc"] = data_anc["GivenServices"]
			sub_data["GivenServices_pnc"] = data_pnc["GivenServices"]
			sub_data["GivenServices_imm"] = data_imm["GivenServices"]
			sub_data["OverDueRate_anc"] = data_anc["OverDueRate"]
			sub_data["OverDueRate_pnc"] = data_pnc["OverDueRate"]
			sub_data["OverDueRate_imm"] = data_imm["OverDueRate"]
			
			status = 2
			if (data_anc["OverDueRate"] and data_anc["OverDueRate"] < 7 and data_anc["OverDueRate"] >2) \
			or (data_pnc["OverDueRate"] and data_pnc["OverDueRate"] < 7 and data_pnc["OverDueRate"] >2) \
			or (data_imm["OverDueRate"] and data_imm["OverDueRate"] < 7 and data_imm["OverDueRate"] >2):
				status = 1

			if (data_anc["OverDueRate"] and data_anc["OverDueRate"] > 7) \
			or (data_pnc["OverDueRate"] and data_pnc["OverDueRate"] > 7) \
			or (data_imm["OverDueRate"] and data_imm["OverDueRate"] > 7):
				status = 0

			if status == 2:
				num_good = num_good + 1
			elif status == 1:
				num_avg = num_avg + 1
			else:
				num_poor = num_poor +1

			sub_data["status"] = status
			sub_data["Subcenter"] = sub.name
			sub_data["SubcenterId"] = sub.id

			AshaDetails = []
			cgs = Beneficiary.objects.all().filter(subcenter = sub).values("caregiver").distinct()
			for cg in cgs:
				if cg["caregiver"]:
					_cg = CareGiver.objects.get(id=cg["caregiver"])
					AshaDetails.append(_cg.first_name+':'+_cg.phone)

			sub_data["AshaDetails"] = AshaDetails
			sub_data["lat"] = sub._lat
			sub_data["long"] = sub._long
			#TODO remove dummy lat, long later
			_lat = 25.619626
			_long = 79.180409
			sign = randint(1,2)
			if sign == 1:
				sub_data["lat"] = _lat + randint(1,100)*0.01
				sub_data["long"] = _long + randint(1,100)*0.01
			else:
				sub_data["lat"] = _lat - randint(1,100)*0.01
				sub_data["long"] = _long - randint(1,100)*0.01

			data.append(sub_data)

	block_data = {}
	block_data["data"] = data
	block_data["summary"] = { "Good":num_good , "Poor":num_poor ,"Average":num_avg }
	block_data["blockid"] = blockid
	block_data["blockname"] = blockname
	
	return HttpResponse(json.dumps(block_data), mimetype="application/json")