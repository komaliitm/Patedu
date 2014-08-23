import requests
import json
from django.conf import settings
from common.utils import utcnow_aware
import pytz
from celery import shared_task

@shared_task
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
	return r.text