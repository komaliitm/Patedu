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
from mcts_transactions.models import DueEvents, ContentDelivered
from sms.sender import SendSMSUnicode

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



