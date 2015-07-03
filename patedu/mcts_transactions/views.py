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
from django.db.models import Q, Count, Max
from django.views.decorators.csrf import csrf_exempt
import sys
from mcts_transactions.models import *
from mcts_identities.models import *
from sms.sender import SendSMSUnicode
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render
from math import ceil
import unicodedata
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required

class StaticData:
	SCHEDULE_MSG =0
	AWARENESS_MSG = 1
	SENDER = 0
	CLEANER = 1
	REACHONLYSELF = 0


def GenerateReportPerVillage(month =None, year=None):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	now_utc = utcnow_aware()
	now = now_utc.astimezone(tz)
	if not month:
		month = now.month
	if not year:
		year = now.year

	f1 = open('MCTSDLPMCS_IMM_SMS_REPORT_PERVILLAGE'+str(month)+', '+str(year), 'w')
	f2 = open('MCTSDLPMCS_ANC_SMS_REPORT_PERVILLAGE'+str(month)+', '+str(year), 'w')
	cds = ContentDelivered.objects.filter(timestamp__year = year, timestamp__month=month, status=0)

	ancReport = {}
	ancNumber = 0
	immReport = {}
	immNumber = 0
	for cd in cds:
		msg_log = unicode(', MSG SENT: ','utf-8').encode('utf8')+cd.msg.encode('utf8')
		msg_log = ('TO:'+cd.benefeciary.notify_number+'-'+cd.benefeciary.first_name+', TYPE:'+Beneficiary.NUMBER_TYPE_REVERSE_MAP[str(cd.benefeciary.notify_number_type)]).encode('utf8')+msg_log
		if ANCBenef.objects.filter(id=cd.benefeciary.id).count() > 0:
			if not cd.benefeciary.subcenter.MCTS_ID in ancReport:
				ancReport[cd.benefeciary.subcenter.MCTS_ID] = []
			ancReport[cd.benefeciary.subcenter.MCTS_ID].append(msg_log)
			ancNumber = ancNumber + 1
		elif IMMBenef.objects.filter(id=cd.benefeciary.id).count() > 0:
			if not cd.benefeciary.subcenter.MCTS_ID in immReport:
				immReport[cd.benefeciary.subcenter.MCTS_ID] = []
			immReport[cd.benefeciary.subcenter.MCTS_ID].append(msg_log)
			immNumber = immNumber + 1
		else:
			continue
	
	# print ancNumber
	# print ancReport
	# print immNumber
	# print immReport

	f2.write("================== ANC SMS REPORT ==================\n")
	f2.write("================== "+ str(month)+', '+str(year) +" ==================\n")
	f2.write("================== TOTAL BENEFECIARIES TOUCHED: "+ str(ancNumber)+" ==================\n")
	for k,v in ancReport.iteritems():
		subcenter = None
		try:
			subcenter = SubCenter.objects.get(MCTS_ID= k)
		except ObjectDoesNotExist:
			continue
		f2.write("\n\n\nDISTRICT: "+subcenter.district.name+"\t BLOCK: "+subcenter.block.name+"\t SUBCENTER: "+subcenter.name+"\n\n")
		i= 1
		for cd in v:
			f2.write("S.No. "+str(i))
			f2.write(": "+cd+"\n")
			i = i + 1

	f1.write("================== IMMUNIZATION SMS REPORT ==================\n")
	f1.write("================== "+ str(month)+', '+str(year) +" ==================\n")
	f1.write("================== TOTAL BENEFECIARIES TOUCHED: "+ str(immNumber)+" ==================\n")
	for k,v in immReport.iteritems():
		subcenter = None
		try:
			subcenter = SubCenter.objects.get(MCTS_ID= k)
		except ObjectDoesNotExist:
			continue
		f1.write("\n\n\nDISTRICT: "+subcenter.district.name+"\t BLOCK: "+subcenter.block.name+"\t SUBCENTER: "+subcenter.name+"\n\n")
		i= 1
		for cd in v:
			f1.write("S.No. "+str(i))
			f1.write(": "+cd+"\n")
			i = i + 1

	f1.close()
	f2.close()

def GenerateReport(month=None, year=None):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	now_utc = utcnow_aware()
	now = now_utc.astimezone(tz)
	if not month:
		month = now.month
	if not year:
		year = now.year

	f1 = open('MCTSDLPMCS_IMM_SMS_REPORT'+str(month)+', '+str(year), 'w')
	f2 = open('MCTSDLPMCS_ANC_SMS_REPORT'+str(month)+', '+str(year), 'w')
	cds = ContentDelivered.objects.filter(timestamp__year = year, timestamp__month=month, status=0)

	i = 0
	j = 0
	for cd in cds:
		if ANCBenef.objects.filter(id=cd.benefeciary.id).count() > 0:
			f = f2
			i = i + 1
			cnt = i
		elif IMMBenef.objects.filter(id=cd.benefeciary.id).count() > 0:
			f = f1
			j = j+1
			cnt = j
		else:
			continue
		f.write(str(cnt)+". ")
		f.write('MSG: '+cd.msg.encode('utf8'))
		f.write(', NUMBER: '+cd.benefeciary.notify_number)
		f.write(', WHOM: self\n') 
	f1.close()
	f2.close()


def SendSchSMS(role=StaticData.SCHEDULE_MSG, job=StaticData.SENDER, reach = StaticData.REACHONLYSELF, month=None, year=None):
	#TODO pick timezone from DB
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	now_utc = utcnow_aware()
	now = now_utc.astimezone(tz)
	if not month:
		month = now.month
	if not year:
		year = now.year

	#if category == StaticData.SCHEDULE_MSG:
	sms_template = u"prelude name की event category इस महीने होनी आवश्यक है. अविलंब आशा बहनजी asha से संपर्क करे. धन्यवाद!"
	
	_allBenefs = Beneficiary.objects.all()
	i=0
	f = open('SMSsendLog', 'w')
	for benef in _allBenefs:
		
		cds = ContentDelivered.objects.filter(benefeciary=benef)
		if cds.count() > 0:
			print 'already sent'
			continue

		if not benef.notify_number or benef.notify_number_type != Beneficiary.NUMBER_TYPE.SELF:
			continue
		benef_number = benef.notify_number
		if len(benef_number) == 11:
			benef_number = benef_number[1:len(benef_number)]
		if int(benef_number) == 0:
			continue

		# #Find all due and unhandled services this month.
		_allDueCurrentMonth = DueEvents.objects.filter(date__year = year, date__month = month, beneficiary= benef)
		event = None
		_numEvents = 0
		for _dueService in _allDueCurrentMonth:
			if not event:
				event = _dueService.event.val
			else:
				event = event +', '+_dueService.event.val
				_numEvents = _numEvents + 1
		if not event:
			continue

		if len(event) > 10:
			event = unicode(event[0:10]) + u" आदि" +unicode(" ("+str(_numEvents)+")")
		else: 
			event = unicode(event)

		if ANCBenef.objects.filter(id=benef.id).count() > 0:
			prelude = u"श्रीमती"
			category = u"जाँच/टीकाकरण"
		elif IMMBenef.objects.filter(id=benef.id).count() > 0:
			prelude = u"बच्चे"
			category = u"टीकाकरण"

		name = unicode(benef.first_name)
		asha_name = u''
		if benef.caregiver:
			asha_name = unicode(benef.caregiver.first_name)
		
		#print unicodedata.normalize('NFKD', asha_name).encode('ascii', 'ignore')

		sms_text = sms_template.replace(u"prelude", prelude).replace(u"name", name).replace(u"category", category).replace(u"event", event).replace(u"asha", asha_name)
		#print sms_text
		sms_msg_hexlified = toHex(sms_text)

		print 'sending Voice Call:'
		
		sms_indicator = "#"+str(i)+": "+benef_number+" : "+ unicodedata.normalize('NFKD', event).encode('ascii', 'ignore') 
		print sms_indicator
		print unicodedata.normalize('NFKD', sms_text).encode('ascii', 'ignore')
		
		#f.write(sms_indicator)
		#f.write(unicodedata.normalize('NFKD', sms_text).encode('ascii', 'ignore'))
		#f.write('\n')

		#sent_code = SendSMSUnicode(recNum=benef_number, msgtxt=sms_msg_hexlified)
		sent_code = 'Status=0'
		#print sent_code
		#f.write(sent_code)
		#f.write('#################################\n')

		i = i +1

		if 'Status=1' in sent_code:
			ContentDelivered.objects.create(msg= sms_text, medium=ContentDelivered.SMS, timestamp = utcnow_aware(), status=1, benefeciary = benef)
		elif 'Status=0' in sent_code:
			ContentDelivered.objects.create(msg= sms_text, medium=ContentDelivered.SMS, timestamp = utcnow_aware(), status=0, benefeciary = benef)	
	f.close()
	return HttpResponse('Succefully sent the SMS', mimetype="application/json")

@login_required
def DashboardPage(request):
	_allBlocks = Block.objects.all()
	blocks = [block for block in _allBlocks]
	return render(request, "dasboard_subcenteratblock.html", {'blocks':blocks})


def GetLastSixMonthsProgress(benefs, sub, reg_type):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)

	ProgressData = [0,0,0,0,0,0]
	this_month_date = today.replace(hour=6, minute=0, second=0, day=1).astimezone(pytz.utc)
	if benefs:
		for month in range(1,6):
			since_date = this_month_date - relativedelta(months=month)

			#TODO: Introduce for new benef registration later
			dues_service = DueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_date.date()) & Q(date__lt=this_month_date.date()) )
			overdues_service = OverDueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_date.date()) & Q(date__lt=this_month_date.date()))
			Overdue = overdues_service.count()

			OverDueRate = 0
			if Overdue > 0:
				#TODO derive sample 
				sample_size = dues_service.count() if dues_service.count() > 0 else benefs.count()
				sample_size = sample_size if sample_size > 0 else 500

				OverDueRate = (float(Overdue)/(month*sample_size))*100

			ProgressData[month-1] = OverDueRate
			this_month_date = since_date
	return ProgressData



def ProcessSubcenterData(benefs, sub, since_months, reg_type, months):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)

	this_month_date = today.replace(hour=6, minute=0, second=0, day=1).astimezone(pytz.utc)

	Overdue = 0
	new_reg = 0
	GivenServices = 0
	OverDueRate = 0
	overdue_services_group = []
	if benefs:
		txs_service = Transactions.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(timestamp__gte=since_months.date())).exclude(event__val=reg_type)
		txs_reg = Transactions.objects.all().filter(Q(subcenter=sub), Q(event__val=reg_type), Q(timestamp__gte=since_months.date()) )
		dues_service = DueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_months.date()) )

		GivenServices = txs_service.count()

		overdues_service = OverDueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_months.date()) )
		overdue_services_group = list(overdues_service.values('event_id').annotate(ods_count=Count('id'), event_name=Max('event__val')))
		Overdue = overdues_service.count()
		new_reg = txs_reg.count()
		
		if Overdue > 0:
			#TODO derive sample 
			sample_size = dues_service.count() if dues_service.count() > 0 else txs_service.count()
			sample_size = sample_size if sample_size > 0 else benefs.count()
			sample_size = sample_size if sample_size > 0 else 500

			OverDueRate = (float(Overdue)/(months*sample_size))*100
	
		if dues_service:
			Adherence = txs_service.count() * 100 / dues_service.count()
		else:
			Adherence = None
		
	else:
		Adherence = None

	ProgressData = GetLastSixMonthsProgress(benefs, sub, reg_type)
	return {
			'Overdue':Overdue,
			'overdue_sg':overdue_services_group,
			'new_reg':new_reg,
			'GivenServices':GivenServices,
			'OverDueRate':OverDueRate,
			'Adherence':Adherence,
			'ProgressData':ProgressData
	}

def get_status(value, cutoff1, cutoff2):
	if value > cutoff2:
		return 0
	elif value >=cutoff1:
		return 1
	else:
		return 2

def increment_count_on_status(value, good, avg, poor):
	if value == 2:
		good = good + 1
	elif value ==1:
		avg = avg + 1
	elif value == 0:
		poor = poor + 1

	return (good, avg, poor)

@login_required
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

	this_month_date = today.replace(hour=6, minute=0, second=0, day=1).astimezone(pytz.utc)
	#process GET params
	since_months = int(request.GET.get('since_months')) if request.GET.get('since_months') else None
	if since_months > 12:
		since_months =12 	
	if since_months:
		months = since_months
		since_months = this_month_date - relativedelta(months=since_months)
	else:
		months = 12
		since_months = this_month_date - relativedelta(months=12)

	data = []
	summary = {"Good":0, "Poor":0, "Average":0}
	summary_anc = {"Good":0, "Poor":0, "Average":0}
	summary_pnc = {"Good":0, "Poor":0, "Average":0}
	summary_imm = {"Good":0, "Poor":0, "Average":0}
	# num_good_anc = 0
	# num_poor_anc = 0
	# num_avg_anc = 0
	# num_good_pnc = 0
	# num_poor_pnc = 0
	# num_avg_pnc = 0
	# num_good_imm = 0
	# num_poor_imm = 0
	# num_avg_imm = 0
	from common.models import AnalyticsData
	from mcts_transactions.tasks import analytics_aggregator_allblocks
	for block in blocks:
		analytics_data = AnalyticsData.objects.filter(block=block, since_months=months, month= this_month_date.month, year=this_month_date.year)
		if not analytics_data:
			analytics_aggregator_allblocks.delay()
			return HttpResponseNotAllowed('Check after 5 mins. Data generation in progress.') 
		data += json.loads(analytics_data[0].data)
		summary["Good"] += json.loads(analytics_data[0].summary)["Good"]
		summary["Poor"] += json.loads(analytics_data[0].summary)["Poor"]
		summary["Average"] += json.loads(analytics_data[0].summary)["Average"]

		summary_anc["Good"] += json.loads(analytics_data[0].summary_anc)["Good"]
		summary_anc["Poor"] += json.loads(analytics_data[0].summary_anc)["Poor"]
		summary_anc["Average"] += json.loads(analytics_data[0].summary_anc)["Average"]

		summary_pnc["Good"] += json.loads(analytics_data[0].summary_pnc)["Good"]
		summary_pnc["Poor"] += json.loads(analytics_data[0].summary_pnc)["Poor"]
		summary_pnc["Average"] += json.loads(analytics_data[0].summary_pnc)["Average"]

		summary_imm["Good"] += json.loads(analytics_data[0].summary_imm)["Good"]
		summary_imm["Poor"] += json.loads(analytics_data[0].summary_imm)["Poor"]
		summary_imm["Average"] += json.loads(analytics_data[0].summary_imm)["Average"]

		# #find all the subcenters in the block
		# subs = SubCenter.objects.filter(block=block)
		# for sub in subs:
		# 	sub_data = {}

		# 	#total beneficiaries.
		# 	anc_benefs = ANCBenef.objects.filter(subcenter = sub)
		# 	pnc_benefs = PNCBenef.objects.filter(subcenter = sub)
		# 	imm_benefs = IMMBenef.objects.filter(subcenter = sub)

		# 	sub_data["Beneficiaries_anc"] = anc_benefs.count()
		# 	sub_data["Beneficiaries_pnc"] = pnc_benefs.count()
		# 	sub_data["Beneficiaries_imm"] = imm_benefs.count()

		# 	data_anc = ProcessSubcenterData(anc_benefs, sub, since_months, Events.ANC_REG_VAL, months)
		# 	data_pnc = ProcessSubcenterData(pnc_benefs, sub, since_months, Events.PNC_REG_VAL, months)
		# 	data_imm = ProcessSubcenterData(imm_benefs, sub, since_months, Events.IMM_REG_VAL, months)

		# 	sub_data["Beneficiaries_anc"] = anc_benefs.count()
		# 	sub_data["Beneficiaries_pnc"] = pnc_benefs.count()
		# 	sub_data["Beneficiaries_imm"] = imm_benefs.count()
		# 	sub_data["Adherence_anc"] = data_anc["Adherence"]
		# 	sub_data["Adherence_pnc"] = data_pnc["Adherence"]
		# 	sub_data["Adherence_imm"] = data_imm["Adherence"]
		# 	sub_data["new_reg_anc"] = data_anc["new_reg"]
		# 	sub_data["new_reg_pnc"] = data_pnc["new_reg"]
		# 	sub_data["new_reg_imm"] = data_imm["new_reg"]
 	# 		sub_data["Overdue_anc"] = data_anc["Overdue"]
		# 	sub_data["Overdue_pnc"] = data_pnc["Overdue"]
		# 	sub_data["Overdue_imm"] = data_imm["Overdue"]
		# 	sub_data["overdue_sg_anc"] = data_anc["overdue_sg"]
		# 	sub_data["overdue_sg_pnc"] = data_pnc["overdue_sg"]
		# 	sub_data["overdue_sg_imm"] = data_imm["overdue_sg"]
		# 	sub_data["GivenServices_anc"] = data_anc["GivenServices"]
		# 	sub_data["GivenServices_pnc"] = data_pnc["GivenServices"]
		# 	sub_data["GivenServices_imm"] = data_imm["GivenServices"]
		# 	sub_data["OverDueRate_anc"] = data_anc["OverDueRate"]
		# 	sub_data["OverDueRate_pnc"] = data_pnc["OverDueRate"]
		# 	sub_data["OverDueRate_imm"] = data_imm["OverDueRate"]
		# 	sub_data["ProgressData_anc"] = data_anc["ProgressData"]
		# 	sub_data["ProgressData_pnc"] = data_pnc["ProgressData"]
		# 	sub_data["ProgressData_imm"] = data_imm["ProgressData"]

		# 	status_anc = get_status(data_anc["OverDueRate"], 5, 7)
		# 	status_pnc = get_status(data_pnc["OverDueRate"], 5, 7)
		# 	status_imm = get_status(data_imm["OverDueRate"], 5, 7)
			
		# 	num_good_anc, num_avg_anc, num_poor_anc = increment_count_on_status(status_anc, num_good_anc, num_avg_anc, num_poor_anc)
		# 	num_good_pnc, num_avg_pnc, num_poor_pnc = increment_count_on_status(status_pnc, num_good_pnc, num_avg_pnc, num_poor_pnc)
		# 	num_good_imm, num_avg_imm, num_poor_imm = increment_count_on_status(status_imm, num_good_imm, num_avg_imm, num_poor_imm) 

		# 	sub_data["status_anc"] = status_anc
		# 	sub_data["status_pnc"] = status_pnc
		# 	sub_data["status_imm"] = status_imm
		# 	from math import ceil
		# 	sub_data["status"] = ceil((status_anc + status_pnc + status_imm)/3 - 0.5)
		# 	sub_data["Subcenter"] = sub.name
		# 	sub_data["SubcenterId"] = sub.id

		# 	AshaDetails = []
		# 	cgs = Beneficiary.objects.all().filter(subcenter = sub).values("caregiver").distinct()
		# 	for cg in cgs:
		# 		if cg["caregiver"]:
		# 			_cg = CareGiver.objects.get(id=cg["caregiver"])
		# 			AshaDetails.append(_cg.first_name+':'+_cg.phone)

		# 	sub_data["AshaDetails"] = AshaDetails
			
		# 	ANMDetails = []
		# 	cps = Beneficiary.objects.all().filter(subcenter = sub).values("careprovider").distinct()
		# 	for cp in cps:
		# 		if cp["careprovider"]:
		# 			_cp = CareProvider.objects.get(id=cp["careprovider"])
		# 			ANMDetails.append(_cp.first_name+':'+_cp.phone)

		# 	sub_data["ANMDetails"] = ANMDetails


		# 	sub_data["lat"] = sub._lat if sub._lat else block._lat
		# 	sub_data["long"] = sub._long if sub._long else block._long

		# 	#TODO remove dummy lat, long later
		# 	#_lat = 25.619626
		# 	#_long = 79.180409
		# 	#sign = randint(1,2)
		# 	#if sign == 1:
		# 	#	sub_data["lat"] = _lat + randint(1,100)*0.01
		# 	#	sub_data["long"] = _long + randint(1,100)*0.01
		# 	#else:
		# 	#	sub_data["lat"] = _lat - randint(1,100)*0.01
		# 	#	sub_data["long"] = _long - randint(1,100)*0.01

		# 	data.append(sub_data)

	block_data = {}
	block_data["data"] = data
	block_data["summary"] = summary
	block_data["summary_anc"] = summary_anc
	block_data["summary_pnc"] = summary_pnc
	block_data["summary_imm"] = summary_imm
	block_data["blockid"] = blockid
	block_data["blockname"] = blockname
	
	return HttpResponse(json.dumps(block_data), mimetype="application/json")
