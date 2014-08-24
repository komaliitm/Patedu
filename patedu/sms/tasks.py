import requests
import json
from django.conf import settings
from common.utils import utcnow_aware
import pytz
from celery import shared_task
from sms.models import LastRetrieveTime
from datetime import timedelta

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

@shared_task
def ReceiveSMSSinceLast():
	timezone = 'Asia/Kolkata'
	tz = pytz.timezone(timezone)
	now_utc = utcnow_aware()
	now = now_utc.astimezone(tz)
	now_date = now.date()

	rets = LastRetrieveTime.objects.filter(status=0)
	if rets: 
		rets = rets.order_by('-last_ret')
		last_ret_utc = rets[0].last_ret
		last_ret = last_ret_utc.astimezone(tz)
		last_ret = last_ret + timedelta(seconds=1)
		sdtime = last_ret.strftime('%Y-%m-%d %H:%M:%S')
	else:
		sdtime = now_date.isoformat()+' 00:00:00'

	edtime = now.strftime('%Y-%m-%d %H:%M:%S')
	print 'sdtime: '+sdtime
	print 'edtime: '+edtime

	url = settings.SMSPROVIDERRECEIVE_URL
	userSmsProvider = settings.SMSPROVIDER_USER
	passSmsProvider = settings.SMSPROVIDER_PASS
	senderId = str(settings.SMSREPLYNUMBER)

	GET_str = '?'+'user='+userSmsProvider+':'+passSmsProvider+'&'+'senderID='+senderId+'&'+'sdtime='+sdtime+'&'+'edtime='+edtime
	GET_url = url+GET_str
	print GET_url
	r = requests.get(GET_url)
	lrt = LastRetrieveTime(last_ret=now_utc)
	print r.text
	if 'Status=0' in r.text:
		lrt.status = 0
	else:
		lrt.status = 1
	lrt.save()
	return r.text