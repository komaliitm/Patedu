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

def SendVoiceCall(rec_num, voice_file, campaign_name='voice_call_mcts'):
	url = settings.VOICECALLPROVIDER_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS

	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'da='+rec_num+\
	'&'+'campaign_name='+campaign_name+'&'+'voice_file='+voice_file
	GET_url = url+GET_str

	print GET_url

	r = requests.get(GET_url)
	return r.text

def connect_customer_to_app(customer_no, callerid, calltype="trans", app_url=None, timelimit=60, timeout=60, callback_url=None, CustomField=None):
    sid = settings.EXOTEL_SID
    token = settings.EXOTEL_TOKEN
    if not app_url:
    	app_url = settings.EXOTEL_APP_URL
    return requests.post('https://twilix.exotel.in/v1/Accounts/{sid}/Calls/connect.json'.format(sid=sid),
        auth=(sid, token),
        data={
            'From': customer_no,
            'CallerId': callerid,
            'CallType': calltype,
            'Url': app_url,
            'TimeLimit': timelimit,
            'TimeOut': timeout,
            'StatusCallback': callback_url,
            'CustomField':CustomField
        })