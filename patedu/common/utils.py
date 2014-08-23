# -*- coding: utf-8 -*-

import base64
import uuid
#from django.contrib.auth.models import User
from django.conf import settings
from datetime import date, datetime, time
from functools import reduce
import sys
import os
import time
import inspect
import colorama
from django.utils.timezone import utc
import json
import inspect
#from vaccination.models import Vaccinations
from django.core.exceptions import ObjectDoesNotExist
import pytz
from schedule_api.models import TaskScheduler

def toHex(s):
    res = ""
    for c in s:
        res += "%04X" % ord(c) #at least 4 hex digits, can be more
    return res

def utcnow_aware():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

def pprint(*arg):    
    if not settings.PPRINT_ENABLE:
        return
    msg = reduce(lambda x,y: str(x)+" "+str(y), arg)
    curframe = inspect.currentframe()
    outerframes = inspect.getouterframes(curframe, 2)
    colorama.init()
    print ("["+getPrintablePathForFile(outerframes[1][1])+" ~"+str(outerframes[1][2])+ "]"),    
    print (colorama.Fore.CYAN + colorama.Style.BRIGHT + str(msg)),
    print(colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL)

def get_a_Uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')


def LoadInitialVaccinesData(orm):

    global HANDLE
    static_dir = settings.STATIC_ROOT
    vaccfile = os.path.join(static_dir, 'common', 'vaccines.txt')
    vaccfile = open(vaccfile, 'r')
    lines = vaccfile.readlines()
    vaccfile.close()
    checkmark("Loading intial vaccines data. It may take few minutes...")
    for line in lines:
        vacc_object = json.loads(line.strip())
        orm.Vaccinations.objects.create(vaccineId=vacc_object["vaccineId"], AgeInWeeks=vacc_object["AgeInWeeks"], VaccineName=vacc_object["VaccineName"], notes=vacc_object["notes"])

def LoadInitialVaccineTemplateData(orm):

    global HANDLE
    static_dir = settings.STATIC_ROOT
    vaccfile = os.path.join(static_dir, 'common', 'vaccine_templates.txt')
    vaccfile = open(vaccfile, 'r')
    lines = vaccfile.readlines()
    vaccfile.close()
    checkmark("Loading intial medicine data. It may take few minutes...")
    for line in lines:
        temp_object = json.loads(line.strip())
        vaccine = None
        try:
            vaccine = orm.Vaccinations.objects.get(vaccineId=temp_object["vaccine"])
        except ObjectDoesNotExist:
            print "Corresponding vaccine is not found"
            return
        orm.VaccineReminderTemplate.objects.create(Vaccine=vaccine, stage=temp_object["stage"], Language=temp_object["Language"], sms_message=temp_object["sms_message"])

def LoadInitialVaccineSMSData(orm):

    global HANDLE
    orm.SMSMessages.objects.create(msg_identifier="VAC_REM_1M", msg=u"आपके बच्चे childName का  vaccineName टीकाकरण अगले महीने date को होनी है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.")
    orm.SMSMessages.objects.create(msg_identifier="VAC_REM_1W", msg=u"आपके बच्चे childName का  vaccineName टीकाकरण अगले सप्ताह date को होनी है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.")
    orm.SMSMessages.objects.create(msg_identifier="VAC_REM_1D", msg=u"आपके बच्चे childName का  vaccineName टीकाकरण अगले दिन date को होनी है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.")
    orm.SMSMessages.objects.create(msg_identifier="OPV_AW", msg=u'कृपया समय पर vaccineName टीकाकरण लीजिये. यह टीका आपके बच्चे को पोलियो रोकने के लिए महत्वपूर्ण है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.')
    orm.SMSMessages.objects.create(msg_identifier="BCG_AW", msg=u'कृपया समय पर vaccineName टीकाकरण लीजिये. यह टीका क्षय रोग से आपके बच्चे को बचाने के लिए महत्वपूर्ण है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.')
    orm.SMSMessages.objects.create(msg_identifier="DPT_AW", msg=u'कृपया समय पर vaccineName टीकाकरण लीजिये. यह टीका टिटनेस से आपके बच्चे को बचाने के लिए महत्वपूर्ण है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.')
    orm.SMSMessages.objects.create(msg_identifier="MSL_AW", msg=u'कृपया समय पर vaccineName टीकाकरण लीजिये. यह टीका खसरा से आपके बच्चे को बचाने के लिए महत्वपूर्ण है. अधिक जानकारी के लिए स्वास्थ्य कार्यकर्ता hwName से बात करें.')
    orm.SMSMessages.objects.create(msg_identifier="VAC_WELCOME",msg=u"ई-आरोग्यम एसएमएस सेवा आप का स्वागत करती है. आपका पंजीकरण सफल रहा है.")
    orm.SMSMessages.objects.create(msg_identifier="REG_FAILURE",msg=u"एसएमएस टीकाकरण पंजीकरण विफल. एसएमएस का प्रारूप गलत था.")
    orm.SMSMessages.objects.create(msg_identifier="UNREG_FAILURE",msg=u"एसएमएस टीकाकरण समाप्ति असफल. एसएमएस का प्रारूप गलत था.")
    orm.SMSMessages.objects.create(msg_identifier="REG_SUCCESS",msg=u"एसएमएस टीकाकरण पंजीकरण सफल. लाभार्थी को समय पर जागरूकता और अनुस्मारक एसएमएस प्राप्त होंगे.")
    orm.SMSMessages.objects.create(msg_identifier="UNREG_SUCCESS",msg=u"एसएमएस टीकाकरण समाप्ति सफल. लाभार्थी को अब कोई भी एसएमएस प्राप्त नहीं होगी.")
    orm.SMSMessages.objects.create(msg_identifier="SMS_FAILURE",msg=u"एसएमएस का प्रारूप गलत है. एसएमएस नजरअंदाज कर दिया है.")
    # static_dir = settings.STATIC_ROOT
    # vaccfile = os.path.join(static_dir, 'common', 'sms_msg.txt')
    # vaccfile = open(vaccfile, 'r')
    # lines = vaccfile.readlines()
    # vaccfile.close()
    # checkmark("Loading intial Vaccine SMS data data. It may take few minutes...")
    # for line in lines:
    #     line = line.decode('utf-8')
    #     msg_object = json.loads(line.strip())
    #     orm.SMSMessagesHindi.objects.create(msg_identifier=msg_object["msg_identifier"], msg=msg_object["msg"])

def LoadInitialScheduleData(orm):

    global HANDLE
    TaskScheduler.schedule_every(task_name='vaccination.views.send_reminders', period='minutes', every='30')

def checkmark(*arg):    

    def getPrintablePathForFile(path):
        filename = os.path.basename(path)
        dirname = os.path.basename(os.path.dirname(path))
        return dirname+"/"+filename
        
    msg = reduce(lambda x,y: str(x)+" "+str(y), arg)
    curframe = inspect.currentframe()
    outerframes = inspect.getouterframes(curframe, 2)
    colorama.init()
    print ("["+getPrintablePathForFile(outerframes[1][1])+" ~"+str(outerframes[1][2])+ "]"),    
    print (colorama.Fore.CYAN + colorama.Style.BRIGHT + str(msg)),
    print(colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL)