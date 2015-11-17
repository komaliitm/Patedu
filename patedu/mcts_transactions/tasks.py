import json
import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib.auth.models import User
from common.utils import pprint, utcnow_aware
import time
from django.http import HttpResponseNotAllowed
import dateutil.parser
from django.core.exceptions import ObjectDoesNotExist
from common.utils import get_a_Uuid, utcnow_aware, toHex
from datetime import datetime, timedelta
from random import randint
import pytz
from celery import shared_task
import sys
from mcts_transactions.models import *
from mcts_identities.models import *
from common.models import AnalyticsData, PopulationData, NHMTargets
from math import ceil
import unicodedata
from dateutil.relativedelta import relativedelta
from mcts_identities.models import District, SubCenter, Block, Beneficiary, ANCBenef, PNCBenef, IMMBenef

@shared_task
def analytics_aggregator_allblocks(district_mcts_id='36', rw=False):
	try:
		district = District.objects.get(MCTS_ID=district_mcts_id)
	except ObjectDoesNotExist:
		print "specified district does not exist"
		return

	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz) 
	
	today_date = today.date()
	anc_cutoff = today_date - timedelta(days=280)
	imm_cutoff = today_date - timedelta(days=365)
	yesterday_utc = today_utc - timedelta(days=1)

	dt_month = today.date().month
	dt_year = today.date().year

	fin_marker = today_date.replace(month = 4, day=1)
	if today_date.month < 4:
		fin_marker = fin_marker.replace(year=today_date.year-1)
	mreg_district_target = NHMTargets.objects.get(target_type='MREG', district=district, target_year=fin_marker.year).target_value
	creg_district_target = NHMTargets.objects.get(target_type='CREG', district=district, target_year=fin_marker.year).target_value
	district_population = PopulationData.objects.get(unit_type=District.__name__, MCTS_ID= district.MCTS_ID, year=fin_marker.year).population

	month_span = [1, 2, 3, 4, 5, 6, 12]
	for months in month_span:
		this_month_date = today.replace(hour=6, minute=0, second=0, day=1).astimezone(pytz.utc)
		since_months = this_month_date - relativedelta(months=(months-1))
		blocks = SubCenter.objects.filter(district=district).values('block_id').distinct()
		for block_entry in blocks:
			block = Block.objects.get(id=block_entry['block_id'])
			if not rw and AnalyticsData.objects.filter(block=block, since_months=months, month= this_month_date.month, year=this_month_date.year):
				continue
			subcenters = SubCenter.objects.filter(block=block)
			data = []
			num_good_anc = 0
			num_poor_anc = 0
			num_avg_anc = 0
			num_exc_anc = 0
			num_good_pnc = 0
			num_poor_pnc = 0
			num_avg_pnc = 0
			num_exc_pnc = 0
			num_good_imm = 0
			num_poor_imm = 0
			num_avg_imm = 0
			num_exc_imm = 0
			for sub in subcenters:
				sub_data = {}

				#total beneficiaries.
				anc_benefs = ANCBenef.objects.filter(subcenter = sub)
				pnc_benefs = PNCBenef.objects.filter(subcenter = sub)
				imm_benefs = IMMBenef.objects.filter(subcenter = sub)

				sub_data["Beneficiaries_anc"] = anc_benefs.filter(LMP__gte=anc_cutoff).count()
				sub_data["Beneficiaries_pnc"] = pnc_benefs.count()
				sub_data["Beneficiaries_imm"] = imm_benefs.filter(dob__gte=imm_cutoff).count()

				from mcts_transactions.views import ProcessSubcenterData, get_status, increment_count_on_status, get_reg_status
				data_anc = ProcessSubcenterData(anc_benefs, sub, since_months, Events.ANC_REG_VAL, months)
				data_pnc = ProcessSubcenterData(pnc_benefs, sub, since_months, Events.PNC_REG_VAL, months)
				data_imm = ProcessSubcenterData(imm_benefs, sub, since_months, Events.IMM_REG_VAL, months)

				mreg_status = 0
				creg_status = 0
				try:
					subc_population = PopulationData.objects.get(unit_type=SubCenter.__name__, MCTS_ID=sub.MCTS_ID, year=fin_marker.year).population
					mreg_target = ceil((mreg_district_target * subc_population) / (district_population) )
					creg_target = ceil((creg_district_target * subc_population) / (district_population) )	
					sub_data["mreg_target"] = mreg_target
					sub_data["creg_target"] = creg_target
					mreg_status = sub_data["Beneficiaries_anc"]/mreg_target if mreg_target else 0 
					creg_target = sub_data["Beneficiaries_imm"]/creg_target if creg_target else 0
				except:
					sub_data["mreg_target"] = 'NA'
					sub_data["creg_target"] = 'NA'
				

				sub_data["Adherence_anc"] = data_anc["Adherence"]
				sub_data["Adherence_pnc"] = data_pnc["Adherence"]
				sub_data["Adherence_imm"] = data_imm["Adherence"]
				sub_data["new_reg_anc"] = data_anc["new_reg"]
				sub_data["new_reg_pnc"] = data_pnc["new_reg"]
				sub_data["new_reg_imm"] = data_imm["new_reg"]
	 			sub_data["Overdue_anc"] = data_anc["Overdue"]
				sub_data["Overdue_pnc"] = data_pnc["Overdue"]
				sub_data["Overdue_imm"] = data_imm["Overdue"]
				sub_data["overdue_sg_anc"] = data_anc["overdue_sg"]
				sub_data["overdue_sg_pnc"] = data_pnc["overdue_sg"]
				sub_data["overdue_sg_imm"] = data_imm["overdue_sg"]
				sub_data["due_sg_anc"] = data_anc["due_sg"]
				sub_data["due_sg_pnc"] = data_pnc["due_sg"]
				sub_data["due_sg_imm"] = data_imm["due_sg"]
				sub_data["given_sg_anc"] = data_anc["given_sg"]
				sub_data["given_sg_pnc"] = data_pnc["given_sg"]
				sub_data["given_sg_imm"] = data_imm["given_sg"]
				sub_data["GivenServices_anc"] = data_anc["GivenServices"]
				sub_data["GivenServices_pnc"] = data_pnc["GivenServices"]
				sub_data["GivenServices_imm"] = data_imm["GivenServices"]
				sub_data["DueServices_anc"] = data_anc["DueServices"]
				sub_data["DueServices_pnc"] = data_pnc["DueServices"]
				sub_data["DueServices_imm"] = data_imm["DueServices"]
				sub_data["OverDueRate_anc"] = data_anc["OverDueRate"]
				sub_data["OverDueRate_pnc"] = data_pnc["OverDueRate"]
				sub_data["OverDueRate_imm"] = data_imm["OverDueRate"]
				sub_data["ProgressData_anc"] = data_anc["ProgressData"]
				sub_data["ProgressData_pnc"] = data_pnc["ProgressData"]
				sub_data["ProgressData_imm"] = data_imm["ProgressData"]

				status_anc, reason_anc = get_status(data_anc["OverDueRate"], 3, 5)
				status_pnc, reason_pnc = get_status(data_pnc["OverDueRate"], 3, 5)
				status_imm, reason_imm = get_status(data_imm["OverDueRate"], 3, 5)

				if sub_data["Beneficiaries_anc"] == 0 or sub_data["DueServices_anc"] < 3:
					if status_anc == 0:
						reason_anc += "& Low beneficiary registration or updation"
					else:
						status_anc = 0
						reason_anc += "But Low beneficiary registration or updation"
				if sub_data["Beneficiaries_pnc"] == 0 or sub_data["DueServices_pnc"] < 3:
					if status_pnc == 0:
						reason_pnc += "& Low beneficiary registration or updation"
					else:
						status_pnc = 0
						reason_pnc += "But Low beneficiary registration or updation"
				if sub_data["Beneficiaries_imm"] == 0 or sub_data["DueServices_imm"] < 3:
					if status_imm == 0:
						reason_imm += "& Low beneficiary registration or updation"
					else:
						status_imm = 0
						reason_imm += "But Low beneficiary registration or updation"

				status_anc, reason_anc = get_reg_status(mreg_status, status_anc, reason_anc, .4, .7)
				status_imm, reason_imm = get_reg_status(creg_status, status_imm, reason_imm, .4, .7)

				num_good_anc, num_avg_anc, num_poor_anc, num_exc_anc = increment_count_on_status(status_anc, num_good_anc, num_avg_anc, num_poor_anc, num_exc_anc)
				num_good_pnc, num_avg_pnc, num_poor_pnc, num_exc_pnc = increment_count_on_status(status_pnc, num_good_pnc, num_avg_pnc, num_poor_pnc, num_exc_pnc)
				num_good_imm, num_avg_imm, num_poor_imm, num_exc_imm = increment_count_on_status(status_imm, num_good_imm, num_avg_imm, num_poor_imm, num_exc_imm) 

				sub_data["status_anc"] = status_anc
				sub_data["status_pnc"] = status_pnc
				sub_data["status_imm"] = status_imm
				sub_data["reason_anc"] = reason_anc
				sub_data["reason_pnc"] = reason_pnc
				sub_data["reason_imm"] = reason_imm
				sub_data["status"] = ceil((status_anc + status_pnc + status_imm)/3 - 0.5)
				sub_data["Subcenter"] = sub.name
				sub_data["SubcenterId"] = sub.id

				AshaDetails = []
				cgs = Beneficiary.objects.all().filter(subcenter = sub).values("caregiver").distinct()
				for cg in cgs:
					if cg["caregiver"]:
						_cg = CareGiver.objects.get(id=cg["caregiver"])
						AshaDetails.append(_cg.first_name+':'+_cg.phone)

				sub_data["AshaDetails"] = AshaDetails
				
				ANMDetails = []
				cps = Beneficiary.objects.all().filter(subcenter = sub).values("careprovider").distinct()
				for cp in cps:
					if cp["careprovider"]:
						_cp = CareProvider.objects.get(id=cp["careprovider"])
						ANMDetails.append(_cp.first_name+':'+_cp.phone)

				sub_data["ANMDetails"] = ANMDetails

				# TODO remove dummy lat, long later
				_lat = block._lat if block._lat else 25.619626 
				_long = block._long if block._long else 79.180409
				sign = randint(1,2)
				if sign == 1:
					_lat = _lat + randint(1,100)*0.005
					_long = _long + randint(1,100)*0.005
				else:
					_lat = _lat - randint(1,100)*0.005
					_long = _long - randint(1,100)*0.005

				sub_data["lat"] = sub._lat if sub._lat else _lat
				sub_data["long"] = sub._long if sub._long else _long

				data.append(sub_data)
			block_data = {}
			block_data["data"] = data
			block_data["summary"] = {"Excellent":num_exc_anc, "Good":num_good_anc , "Poor":num_poor_anc ,"Average":num_avg_anc }	
			block_data["summary_anc"] = {"Excellent":num_exc_anc, "Good":num_good_anc , "Poor":num_poor_anc ,"Average":num_avg_anc }
			block_data["summary_pnc"] = {"Excellent":num_exc_pnc, "Good":num_good_pnc , "Poor":num_poor_pnc ,"Average":num_avg_pnc }
			block_data["summary_imm"] = {"Excellent":num_exc_imm, "Good":num_good_imm , "Poor":num_poor_imm ,"Average":num_avg_imm }
			block_data["blockid"] = block.id
			block_data["blockname"] = block.name
			existing_analytics = AnalyticsData.objects.filter(block=block, since_months=months, month= this_month_date.month, year=this_month_date.year)
			if existing_analytics:
				existing_analytics.delete()

			print "adding: "+str(block.id)+" , "+"months "
			ad = AnalyticsData.objects.create(block = block, data = json.dumps(block_data["data"]), summary=json.dumps(block_data["summary"]),\
		 		summary_anc=json.dumps(block_data["summary_anc"]), summary_imm=json.dumps(block_data["summary_imm"]),\
		 		summary_pnc=json.dumps(block_data["summary_pnc"]), since_months = months, month = this_month_date.month, year=this_month_date.year)
