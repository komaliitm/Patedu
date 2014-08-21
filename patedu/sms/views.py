# Create your views here.
import requests
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
import pytz
from common.utils import *

#Make a class (with model) SMS with non-HTTP functions for Send and receive.
#Make a class and model for the POST parameters.

def SendSMSWrapper(request):
	return SendSMS(recNum=9390681183, msgtxt='This is dlpmcs Test SMS beedu')

def ReplyResponse(request):
	fromNumber = request.GET.get('da')
	msgtxt = request.GET.get('msgtxt')

	print fromNumber + ' : ' +msgtxt 
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