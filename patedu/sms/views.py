# Create your views here.
import requests
from django.utils import simplejson as json
from django.conf import settings

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
	r = requests.get(GET_url)
	return HttpResponse(r)

def SendSMSUnicode(recNum, msgtxt, state=4):
	url = settings.SMSPROVIDER_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = settings.SMSSENDERID
	
	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'receipientno='+str(recNum)+'&'+'msgtxt='+msgtxt+'&'+'state='+str(state)+'&msgtype=4&dcs=8&ishex=1'
	GET_url = url+GET_str
	r = requests.get(GET_url)
	return HttpResponse(r)

def ReceiveSMS(request):
	smsReceiveURL = 'http://api.mVaayoo.com/mvaayooapi/MessageReply?user=komalvis007g@gmail.com:babboo&senderID=562639831&receipientno=9390681183&sdtime=2013-07-14 00:00:00&edtime=2013-07-15 00:00:00'
	r = requests.get(smsReceiveURL)
	return HttpResponse(r)