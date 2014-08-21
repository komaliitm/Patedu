# Create your views here.
import requests
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
import pytz
from common.utils import *
import dateutil.parser
from sms.models import IncomingSMS

#Make a class (with model) SMS with non-HTTP functions for Send and receive.
#Make a class and model for the POST parameters.

def SendSMSWrapper(request):
	return SendSMS(recNum=9390681183, msgtxt='This is dlpmcs Test SMS beedu')

def ReplyResponse(request):
	sender_num = request.GET.get('da')
	msgtxt = request.GET.get('msgtxt')
	dtime = dateutil.parser.parse(request.GET.get('time'))


	#REG V 9390681183 03/12/87; UNREG V 9390681183; UPDATE V 9390681183 03/12/87
	msg_identifiers = msgtxt.split('+')
	params = True
	if msg_identifiers[1] != 'V'
		params = False
		msg = "Keyword 'V' is missing"

	benef_num = msg_identifiers[2]
	if params and (len(benef_num) == 10 or len(benef_num) == 12):
		try:
			temp = (int)benef_num
		except:
			params = False
			msg = 'Phone number is not correct'
	else:
		params = False
		msg = 'Phone number is not correct'

	dob = ''
	if params and msg_identifiers.count() >3:
		dob = msg_identifiers[3]
		try:
			dob = dateutil.parser.parse(dob)
		except:
			params= False
			msg = 'dob is not correct'

	if not params:
		SendSMSUnicode(sender_num, 'SMS format is not correct. '+msg)
	else:		 
		if msg_identifiers[0] == 'REG':
			if dob == '':
				params = False
				SendSMSUnicode(sender_num, 'SMS format is not correct. '+'DOB is not present')
			else:	
				VaccinationBeneficiary.objects.create(NotifyNumber = benef_num, ChildName=' ', Dob=dob, isVerified=True)
		elif msg_identifiers[0] == 'UNREG':
			recs = VaccinationBeneficiary.objects.filter(NotifyNumber = benef_num)
			if recs.count() > 0
				recs[0].delete()

	if params:
		SendSMSUnicode(sender_num, 'Success')
	
	IncomingSMS.objects.create(sender_num=sender_num, msgtxt=msgtxt, dtime=dtime, processed=True)

	return HttpResponse('status=0 <success>')

def SendSMS(recNum, msgtxt, state=4):
	url = settings.SMSPROVIDER_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = settings.SMSSENDERID
	
	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'receipientno='+str(recNum)+'&'+'msgtxt='+msgtxt+'&'+'state='+str(state)
	GET_url = url+GET_str
	r = requests.get(GET_url)
	return r.text

def SendSMSUnicode(recNum, msgtxt, state=4):
	url = settings.SMSPROVIDER_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = settings.SMSSENDERID
	
	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'receipientno='+str(recNum)+'&'+'msgtxt='+msgtxt+'&'+'state='+str(state)+'&msgtype=4&dcs=8&ishex=1'
	GET_url = url+GET_str
	
	print GET_url

	r = requests.get(GET_url)
	return r.text

def ReceiveSMSToday():
	url = settings.SMSPROVIDERRECEIVE_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = str(settings.SMSREPLYNUMBER)

	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	today_utc = utcnow_aware()
	today = today_utc.astimezone(tz)
	today_date = today.date()
	sdtime = today_date.isoformat()+' 00:00:00'
	edtime = today_date.isoformat()+' 23:59:59'

	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'sdtime='+sdtime+'&'+'edtime='+edtime
	GET_url = url+GET_str
	print GET_url
	r = requests.get(GET_url)
	print r.text
	print r.json
	return r.json