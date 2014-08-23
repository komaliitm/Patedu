# Create your views here.
import requests
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
import pytz
from common.utils import *
import dateutil.parser
from sms.models import IncomingSMS
from sms.sender import SendSMSUnicode
from vaccination.models import VaccinationBeneficiary
from vaccination.views import generate_schedule, send_instant_msg
from random import randint
import sys
#Make a class (with model) SMS with non-HTTP functions for Send and receive.
#Make a class and model for the POST parameters.

def SendSMSWrapper(request):
	return SendSMS(recNum=9390681183, msgtxt='This is dlpmcs Test SMS beedu')

def SendSMS(recNum, msgtxt, state=4):
	url = settings.SMSPROVIDER_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = settings.SMSSENDERID
	
	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'receipientno='+str(recNum)+'&'+'msgtxt='+msgtxt+'&'+'state='+str(state)
	GET_url = url+GET_str
	print GET_url
	# r = requests.get(GET_url)
	#return r.text

def ReplyResponse(request):
	sender_num = request.GET.get('da')
	msgtxt = request.GET.get('msgtxt')
	dtime = dateutil.parser.parse(request.GET.get('dtime'))

	err = ''
	action = 3
	#REG V 9390681183 03/12/87; UNREG V 9390681183; UPDATE V 9390681183 03/12/87
	msg_identifiers = msgtxt.split(' ')
	
	params = True

	if len(msg_identifiers) > 0 and msg_identifiers[0] == 'REG': action = 0
	if len(msg_identifiers) > 0 and msg_identifiers[0] == 'UNREG': action = 1

	if len(msg_identifiers) < 3 or len(msg_identifiers) > 4:
		params = False
		err = 'FORMAT ERROR: Minimum expected words is 3'

	if params and msg_identifiers[1] != 'V':
		params = False
		err = "FORMAT ERROR: Type keyword not correct"

	benef_num = ''
	if params and (len(msg_identifiers[2]) == 10 or len(msg_identifiers[2]) == 12):
		try:
			benef_num = msg_identifiers[2]
			temp = int(benef_num)
		except:
			params = False
			err = 'FORMAT ERROR: Phone number should strictly be all numbers'
	else:
		params = False
		err = 'FORMAT ERROR: Phone number does not meet length criteria'

	dob = ''
	if params and len(msg_identifiers) >3:
		dob = msg_identifiers[3]
		try:
			dob = dateutil.parser.parse(dob)
		except:
			params= False
			err = 'FORMAT ERROR: dob is not correct'

	platform = sys.platform
	welcome_msg_id = 'VAC_WELCOME'
	if params:		 
		if action == 0: 
			if dob == '':
				params = False
				err = 'FORMAT ERROR: Dob mising which is reqiured for registration'
			else:	
				if VaccinationBeneficiary.objects.filter(NotifyNumber = benef_num, Dob=dob).count() == 0:
					benef = VaccinationBeneficiary(BeneficiaryId = get_a_Uuid(), NotifyNumber = benef_num, ChildName='', Dob=dob, isVerified=True, CreatedOn = utcnow_aware(), ModifiedOn = utcnow_aware(), VerificationCode = randint(1000, 9999))
					benef.save()
					generate_schedule(benef.BeneficiaryId)
					if platform == 'linux2':
						result = send_instant_msg.delay(benef.NotifyNumber, welcome_msg_id)
					else:
						result = send_instant_msg(benef.NotifyNumber, welcome_msg_id)
		elif action == 1:
			recs = VaccinationBeneficiary.objects.filter(NotifyNumber = benef_num)
			if type(dob).__name__ == 'datetime':
				recs = recs.filter(Dob=dob.date()) 
			if recs.count() > 0:
				recs.delete()
		else:
			params = False
			err = 'FORMAT ERROR: Action keyword received in SMS is wrong'

	if not params:
		if action == 0:
			msg_id = 'REG_FAILURE'
		elif action == 1:
			msg_id = 'UNREG_FAILURE'
		else:
			msg_id = 'SMS_FAILURE'
	else:
		if action == 0:
			msg_id = 'REG_SUCCESS'
		elif action == 1:
			msg_id = 'UNREG_SUCCESS'

	if platform == 'linux2':
		result = send_instant_msg.delay(sender_num, msg_id)
	else:
		result = send_instant_msg(sender_num, msg_id)
	print result
	
	IncomingSMS.objects.create(sender_num=sender_num, msgtxt=msgtxt, dtime=dtime, processed=True, remark=err)
	return HttpResponse('status=0 <success>')