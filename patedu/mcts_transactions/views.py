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
from sms.sender import SendSMSUnicode, connect_customer_to_app
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
from common.models import ANCReportings, IMMReportings


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
	return render(request, "dashboard_base.html", {})

def SubcenterPage(request):
	_allBlocks = Block.objects.all()
	blocks = [block for block in _allBlocks]
	return render(request, "subcenter_page.html", {'blocks':blocks})	

def BlockPage(request):
	return render(request, "block_page.html", {})

def substract_months(date1, date2):
	if date1.year == date2.year:
		return date1.month - date2.month
	else:
		return (date1.month - date2.month) + 12 * (date1.year - date2.year)

def OutreachData(request):
	today_date = utcnow_aware().date()
	this_month_date = today_date.replace(day=1)

	if request.method == 'GET':
		district_mcts_id = str(request.GET.get('district_mcts_id')) if request.GET.get('district_mcts_id') else '36'
		try:
			district = District.objects.get(MCTS_ID=district_mcts_id)
		except:
			return HttpResponseBadRequest('Wrong district id specified')
		months_back = int(request.GET.get('months_back')) if request.GET.get('months_back') else 0
		
		#
		blocks = Block.objects.filter(subcenters__district=district).distinct()
		outreach_anm = []
		outreach_asha = []
		outreach_benef = []
		for block in blocks:
			anm_outreach_data = {}
			asha_outreach_data = {}
			benef_outreach_data = {}
			anm_outreach_data['name'] = block.name.upper()
			anm_outreach_data['scheduled'] = 0
			anm_outreach_data['sent'] = 0
			anm_outreach_data['answered'] = 0
			asha_outreach_data['name'] = block.name.upper()
			asha_outreach_data['scheduled'] = 0
			asha_outreach_data['sent'] = 0
			asha_outreach_data['answered'] = 0
			benef_outreach_data['name'] = block.name.upper()
			benef_outreach_data['scheduled'] = 0
			benef_outreach_data['sent'] = 0
			benef_outreach_data['answered'] = 0
			
			subcenters = SubCenter.objects.filter(block=block)
			subcenters_anm = []
			subcenters_asha = []
			subcenters_benef = []
			for subcenter in subcenters:
				#Calculate seprately, for this subcenter calls stats in each area
				dict = {
					'name':subcenter.name,
					'scheduled':0,
					'sent':0,
					'answered':0
				}
				subcenters_anm.append(dict)
				subcenters_asha.append(dict)
				subcenters_benef.append(dict)
			anm_outreach_data['subcenter'] = subcenters_anm
			asha_outreach_data['subcenter'] = subcenters_asha
			benef_outreach_data['subcenter'] = subcenters_benef
			outreach_anm.append(anm_outreach_data)
			outreach_asha.append(asha_outreach_data)
			outreach_benef.append(benef_outreach_data)
		outreach ={
			'anm':outreach_anm,
			'asha':outreach_asha,
			'benef':outreach_benef
		}
		return HttpResponse(json.dumps(outreach),  mimetype='application/json')
	else:
		return HttpResponseBadRequest('HTTP method type not allowed')

def BlockIndicesData(request):
	today_date = utcnow_aware().date()
	fin_marker = today_date.replace(month = 4, day=1)
	if today_date.month < 4:
		fin_marker = fin_marker.replace(year=today_date.year-1)
	this_month_date = today_date.replace(day=1)
	months_since_start = (this_month_date.month-fin_marker.month) if this_month_date.month > 3 else (this_month_date.month-fin_marker.month + 12) 

	last_year_date = this_month_date.replace(year=this_month_date.year-1)

	months_since_last_year = substract_months(this_month_date, last_year_date)

	mother_reg = [] #{block id, name, count, target, %, sorted}
	child_reg = [] #{block id,name, count, target, %, sorted}
	full_imm = [] #{block id,name, count, target, %, sorted}
	full_anc = [] #{block id,name, count, target, %, sorted}
	del_rep = [] #{block id,name, count, target, %, sorted}

	if request.method == 'GET':
		district_mcts_id = str(request.GET.get('district_mcts_id')) if request.GET.get('district_mcts_id') else '36'
		try:
			district = District.objects.get(MCTS_ID=district_mcts_id)
		except:
			return HttpResponseBadRequest('Wrong district id specified')
		from common.models import NHMTargets, PopulationData
		#Find all distinct blocks
		blocks = Block.objects.filter()
		#query to get all beneficiaries of  given financial year & given iterative block
		for block in blocks:
			imm_benefs = IMMBenef.objects.filter(subcenter__block=block, dob__gte=last_year_date)
			anc_benefs = ANCBenef.objects.filter(subcenter__block=block, LMP__gte=last_year_date)

			mreg_district_target = NHMTargets.objects.get(target_type='MREG', district=district, target_year=fin_marker.year).target_value
			creg_district_target = NHMTargets.objects.get(target_type='CREG', district=district, target_year=fin_marker.year).target_value

			district_population = PopulationData.objects.get(unit_type=District.__name__, MCTS_ID= district.MCTS_ID, year=fin_marker.year).population
			block_population = PopulationData.objects.get(unit_type=Block.__name__, MCTS_ID=block.MCTS_ID, year=fin_marker.year).population

			mreg_target = ceil((mreg_district_target * block_population) / (district_population) )
			creg_target = ceil((creg_district_target * block_population) / (district_population) )

			# imm_benefs_last_year = IMMBenef.objects.filter(subcenter__block=block, dob__year=last_year_date.year, dob__month=last_year_date.month)
			# anc_benefs_last_year = ANCBenef.objects.filter(subcenter__block=block, LMP__year=last_year_date.year, LMP__month=last_year_date.month)
			
			imm_benefs_last_year = imm_benefs
			anc_benefs_last_year = anc_benefs

			# fimm_target = imm_benefs_last_year.count()
			# fanc_target = anc_benefs_last_year.count()
			# drep_target = fanc_target

			fimm_target = imm_benefs.count()
			fanc_target = anc_benefs.count()
			drep_target = ceil(mreg_target * 0.9)

			anc_reports = ANCReportings.objects.filter(benef__in=anc_benefs_last_year)
			fanc_reportings = anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=False,\
			 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=True, anc2_date__isnull=False, anc3_date__isnull=False,\
			 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=True, anc3_date__isnull=False,\
			 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=True,\
			 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=False,\
			 anc4_date__isnull=True)
			fanc_count = fanc_reportings.count()

			imm_reports = IMMReportings.objects.filter(benef__in=imm_benefs_last_year)
			fimm_reportings = imm_reports.filter(measles_date__isnull=False)
			fimm_count = fimm_reportings.count()

			drep_count = anc_reports.filter(delivery_date__isnull=False).count()

			mreg = {
				'block_id':block.MCTS_ID,
				'block_name':block.name,
				'count':anc_benefs.count(),
				'target':mreg_target,
				'percent': (float(anc_benefs.count())/float(mreg_target))*100 if mreg_target else 0
			}
			creg = {
				'block_id':block.MCTS_ID,
				'block_name':block.name,
				'count':imm_benefs.count(),
				'target':creg_target,
				'percent': (float(imm_benefs.count())/float(creg_target))*100 if creg_target else 0
			}
			fanc = {
				'block_id':block.MCTS_ID,
				'block_name':block.name,
				'count':fanc_count,
				'target':fanc_target,
				'percent':(float(fanc_count)/float(fanc_target))*100 if fanc_target else 0
			}
			fimm = {
				'block_id':block.MCTS_ID,
				'block_name':block.name,
				'count':fimm_count,
				'target':fimm_target,
				'percent':(float(fimm_count)/float(fimm_target))*100 if fimm_target else 0
			}
			drep = {
				'block_id':block.MCTS_ID,
				'block_name':block.name,
				'count':drep_count,
				'target':drep_target,
				'percent':(float(drep_count)/float(drep_target))*100 if drep_target else 0
			}
			mother_reg.append(mreg)
			child_reg.append(creg)
			full_imm.append(fimm)
			full_anc.append(fanc)
			del_rep.append(drep)

		mother_reg = sorted(mother_reg, key=lambda k:k.get("percent"), reverse=True)
		child_reg = sorted(child_reg, key=lambda k:k.get("percent"), reverse=True)
		full_imm = sorted(full_imm, key=lambda k:k.get("percent"), reverse=True)
		full_anc = sorted(full_anc, key=lambda k:k.get("percent"), reverse=True)
		del_rep = sorted(del_rep, key=lambda k:k.get("percent"), reverse=True)
		#Prepare data: block name, count(), target, % sorted on %.
		#Preapre data: y-axis [index, block_name], x-axis [%, index]

		block_data = {
			"mother_reg":mother_reg, #{block id, name, count, target, %, sorted}
			"child_reg":child_reg,
			"full_imm":full_imm,
			"full_anc":full_anc,
			"del_rep":del_rep
		}

		mother_reg_graph_x = [[x.get("percent"), i] for i,x in enumerate(mother_reg)]
		mother_reg_graph_y = [[i, x.get("block_name")] for i,x in enumerate(mother_reg)]

		child_reg_graph_x = [[x.get("percent"), i] for i,x in enumerate(child_reg)]
		child_reg_graph_y = [[i, x.get("block_name")] for i,x in enumerate(child_reg)]

		full_imm_graph_x = [[x.get("percent"), i] for i,x in enumerate(full_imm)]
		full_imm_graph_y = [[i, x.get("block_name")] for i,x in enumerate(full_imm)]

		full_anc_graph_x = [[x.get("percent"), i] for i,x in enumerate(full_anc)]
		full_anc_graph_y = [[i, x.get("block_name")] for i,x in enumerate(full_anc)]

		del_rep_graph_x = [[x.get("percent"), i] for i,x in enumerate(del_rep)]
		del_rep_graph_y = [[i, x.get("block_name")] for i,x in enumerate(del_rep)]

		block_graph_data = {
			"mother_reg_chart" : [mother_reg_graph_x, mother_reg_graph_y],
			"child_reg_chart" : [child_reg_graph_x, child_reg_graph_y], 
			"full_anc_chart" : [full_anc_graph_x, full_anc_graph_y],
			"full_imm_chart" : [full_imm_graph_x, full_imm_graph_y],
			"del_rep_chart" : [del_rep_graph_x, del_rep_graph_y]
		}

		imm_benefs = IMMBenef.objects.filter(subcenter__district=district, dob__gte=last_year_date)
		anc_benefs = ANCBenef.objects.filter(subcenter__district=district, LMP__gte=last_year_date)

		mreg_district_target_annual = NHMTargets.objects.get(target_type='MREG', district=district, target_year=fin_marker.year).target_value
		creg_district_target_annual = NHMTargets.objects.get(target_type='CREG', district=district, target_year=fin_marker.year).target_value

		mreg_district_target = ceil((mreg_district_target_annual))
		creg_district_target = ceil((creg_district_target_annual))

		# imm_benefs_last_year = IMMBenef.objects.filter(subcenter__district=district, dob__year=last_year_date.year, dob__month=last_year_date.month)
		# anc_benefs_last_year = ANCBenef.objects.filter(subcenter__district=district, LMP__year=last_year_date.year, LMP__month=last_year_date.month)
		imm_benefs_last_year = imm_benefs
		anc_benefs_last_year = anc_benefs		

		fimm_target = imm_benefs.count()
		fanc_target = anc_benefs.count()
		drep_target = ceil(mreg_district_target * 0.9)
		
		# fimm_target = imm_benefs_last_year.count()
		# fanc_target = anc_benefs_last_year.count()
		# drep_target = fanc_target

		anc_reports = ANCReportings.objects.filter(benef__in=anc_benefs_last_year)
		fanc_reportings = anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=False,\
		 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=True, anc2_date__isnull=False, anc3_date__isnull=False,\
		 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=True, anc3_date__isnull=False,\
		 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=True,\
		 anc4_date__isnull=False) | anc_reports.filter( anc1_date__isnull=False, anc2_date__isnull=False, anc3_date__isnull=False,\
		 anc4_date__isnull=True)
		fanc_count = fanc_reportings.count()

		imm_reports = IMMReportings.objects.filter(benef__in=imm_benefs_last_year)
		fimm_reportings = imm_reports.filter(measles_date__isnull=False)
		fimm_count = fimm_reportings.count()

		drep_count = anc_reports.filter(delivery_date__isnull=False).count()

		mother_reg = {
			'district_id':district.MCTS_ID,
			'district_name':district.name,
			'count':anc_benefs.count(),
			'target':mreg_district_target,
			'percent': (float(anc_benefs.count())/float(mreg_district_target))*100 if mreg_district_target else 0
		}

		child_reg = {
			'district_id':district.MCTS_ID,
			'district_name':district.name,
			'count':imm_benefs.count(),
			'target':creg_district_target,
			'percent': (float(imm_benefs.count())/float(creg_district_target))*100 if creg_district_target else 0
		}
		full_imm = {
			'district_id':district.MCTS_ID,
			'district_name':district.name,
			'count':fimm_count,
			'target':fimm_target,
			'percent':(float(fimm_count)/float(fimm_target))*100 if fimm_target else 0	
		} 
		full_anc = {
			'district_id':district.MCTS_ID,
			'district_name':district.name,
			'count':fanc_count,
			'target':fanc_target,
			'percent':(float(fanc_count)/float(fanc_target))*100 if fanc_target else 0	
		} 
		del_rep = {
			'district_id':district.MCTS_ID,
			'district_name':district.name,
			'count':drep_count,
			'target':drep_target,
			'percent':(float(drep_count)/float(drep_target))*100 if drep_target else 0
		} 

		district_data = {
			"mother_reg":mother_reg, #{block id, name, count, target, %, sorted}
			"child_reg":child_reg,
			"full_imm":full_imm,
			"full_anc":full_anc,
			"del_rep":del_rep
		}

		data = {
			'district_data':district_data,
			'block_graph_data':block_graph_data,
			'block_data':block_data
		}

		return HttpResponse(json.dumps(data),  mimetype='application/json')
	else:
		return HttpResponseBadRequest('Method type not allowed. Only get is allowed.')

def OutreachMonitoringPage(request):
	return render(request, "outreach_page.html", {})

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
	DueServices = 0
	OverDueRate = 0
	overdue_services_group = []
	due_srvices_group = []
	given_services_group = []
	if benefs:
		txs_service = Transactions.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(timestamp__gte=since_months.date())).exclude(event__val=reg_type)
		txs_reg = Transactions.objects.all().filter(Q(subcenter=sub), Q(event__val=reg_type), Q(timestamp__gte=since_months.date()) )
		dues_service = DueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_months.date()) )

		GivenServices = txs_service.count()
		DueServices = dues_service.count()

		overdues_service = OverDueEvents.objects.all().filter(Q(subcenter=sub), Q(beneficiary__in = benefs), Q(date__gte=since_months.date()) )
		overdue_services_group = list(overdues_service.values('event_id').annotate(ods_count=Count('id'), event_name=Max('event__val')))
		given_services_group = list(txs_service.values('event_id').annotate(ods_count=Count('id'), event_name=Max('event__val')))
		due_srvices_group = list(dues_service.values('event_id').annotate(ods_count=Count('id'), event_name=Max('event__val')))
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
			'DueServices':DueServices,
			'overdue_sg':overdue_services_group,
			'due_sg':due_srvices_group,
			'given_sg':given_services_group,
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
			continue
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
	block_data = {}
	block_data["data"] = data
	block_data["summary"] = summary
	block_data["summary_anc"] = summary_anc
	block_data["summary_pnc"] = summary_pnc
	block_data["summary_imm"] = summary_imm
	block_data["blockid"] = blockid
	block_data["blockname"] = blockname
	
	return HttpResponse(json.dumps(block_data), mimetype="application/json")

def ODSANMANC(request):
	if request.method == 'GET':
		anm_id = request.GET.get('CustomField')
		if not anm_id:
			return HttpResponseBadRequest('ANM ID is not provided')
		try:
			anm = CareProvider.objects.get(id=int(anm_id))
		except:
			return HttpResponseBadRequest('ANM does not exist')

		timezone = 'Asia/Kolkata'
		tz = pytz.timezone(timezone)
		today = utcnow_aware().replace(tzinfo=tz)
		date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
		
		#All ANC overdue services for given ANM
		from django.db.models import Count
		anc_benefs = ANCBenef.objects.filter(careprovider=anm)
		anc_ods = OverDueEvents.objects.filter(beneficiary__in=anc_benefs).values('event').annotate(count=Count('event'))

		anm_stats_anc = ''
		for anc_od in anc_ods:
			if anm_stats_anc:
				anm_stats_anc +='. '
			event = Events.objects.get(id=anc_od.get('event'))
			event_count = anc_od.get('count')
			anm_stats_anc += event.val+' '+str(event_count)+' Overdue!'
		return HttpResponse(anm_stats_anc, content_type='text/plain')
	else:
		return HttpResponseBadRequest('HTTP method type not allowed')

def ServicesStringGenerator(qs, type):
	if type == 'ds':
		stats = 'Due Services: '
	else:
		stats = 'Overdue Services: '

	stats = ''
	for q in qs:
		event = Events.objects.get(id=q.get('event'))
		event_count = q.get('count')
		stats += event.val+' '+str(event_count)
		stats += ' '

	stats +='\n'
	return stats

def services_processor(benefs, type, mode=0):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today = utcnow_aware().replace(tzinfo=tz)
	date_then = today.replace(hour=12, minute=0, day=1, second=0).date()

	services_string = ''
	ods = OverDueEvents.objects.filter(beneficiary__in=benefs, date=date_then)
	if mode:
		ods_services= ods.values('event').annotate(count=Count('event'))
		services_string += ServicesStringGenerator(ods_services, 'ods')
	count = ods.count()
	if type == 'ds':
		ds = DueEvents.objects.filter(beneficiary__in=benefs, date=date_then)
		count +=ds.count()
		if mode:
			ds_services = ds.values('event').annotate(count=Count('event'))
			services_string += ServicesStringGenerator(ds_services, 'ds')
	
	return count, services_string

def CallWrapper_Exotel(id, role, type, demo_phone="09390681183"):
	try:
		if role == 'ANM':
			anm = CareProvider.objects.get(id=int(id))
			phone = anm.phone
			benefs = Beneficiary.objects.filter(careprovider=anm)
			count, string = services_processor(benefs=benefs, type=type, mode=1)
		else:
			asha = CareGiver.objects.get(id=int(id))
			phone = asha.phone
			benefs = Beneficiary.objects.filter(caregiver=asha)
			count, string = services_processor(benefs=benefs, type=type, mode=1)
	except:
		return 'ANM/ASHA does not exist'
	sms_text = u"आपके क्षेत्र में शेष सर्विसेज- \n"+unicode(string)+u"प्रेषक,\n मुख्य चिकित्साधिकारी, झाँसी"
	#Send SMS
	SendSMSUnicode(recNum=demo_phone, msgtxt=string)
	#Send Exotel Call here
	custom_field = str(id)+"_"+role+"_"+type
	connect_customer_to_app(customer_no=demo_phone, callerid="01130017630", CustomField=custom_field)


def ServicesCount(request):
	if request.method == 'GET':
		callee = request.GET.get('CustomField')
		if not callee:
			return HttpResponseBadRequest('Callee is not provided')
		
		parameters = callee.split('_')
		id = parameters[0]
		role = parameters[1].upper()
		type = parameters[2].lower()

		try:
			if role == 'ANM':
				anm = CareProvider.objects.get(id=int(id))
				benefs = Beneficiary.objects.filter(careprovider=anm)
				count, string = services_processor(benefs, type)
			else:
				asha = CareGiver.objects.get(id=int(id))
				benefs = Beneficiary.objects.filter(caregiver=asha)
				count, string = services_processor(benefs, type)
		except:
			return HttpResponseBadRequest('ANM/ASHA does not exist')
		
		return HttpResponse(str(count), content_type='text/plain')

def GenerateWorkplan(subcenter, report_type, since_months):
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today = utcnow_aware().replace(tzinfo=tz)
	date_this = today.replace(hour=12, minute=0, day=1, second=0).date()
	date_then = date_this - relativedelta(months=(since_months-1))

	benefs = report_type.objects.filter(subcenter = subcenter, odue_events__date__gte=date_then).distinct() | report_type.objects.filter(subcenter = subcenter, due_events__date__gte=date_then).distinct()
	workplan = [benef.json(date_then) for benef in benefs]
	data = {
		'workplan':workplan,
		'subcenter':subcenter.json(),
		'since_months':since_months,
		'date_then':date_then.isoformat(),
		'date_this':date_then.isoformat(),
		'area':report_type.TYPE
	}
	return data

def SubcWorkplan(request):
	if request.method == 'GET':
		subc_id = request.GET.get('subc_id')
		domain = request.GET.get('report_type')
		since_months = int(request.GET.get('since_months')) if request.GET.get('since_months') else 1

		if not subc_id or not domain:
			return HttpResponseBadRequest('Details not specified properly')
		try:
			subcenter = SubCenter.objects.get(id=int(subc_id))
		except:
			return HttpResponseBadRequest('Subcenter specified is not correct')

		report_type = ANCBenef
		if type == 'IMM':
			report_type = IMMBenef

		data = GenerateWorkplan(subcenter, report_type, since_months)
		return HttpResponse(json.dumps(data), mimetype='application/json')
	else:
		return HttpResponseBadRequest('HTTP method type not allowed')