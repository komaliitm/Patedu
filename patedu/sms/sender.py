import requests
from django.conf import settings

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