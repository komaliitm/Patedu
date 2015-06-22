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
import requests, re

def BuildCallMap(rs):
    rsp = {}
    for r in rs:
        number = re.search(',(\d{10,12})', r).group(0)[1:]
        if len(number) == 11:
            number = number[1:]
        elif len(number) ==12:
            number = number[2:]
        status = int(re.search('\d+$', r).group(0).strip())
        rsp[number] = status
    return rsp

def FindActiveFromIVR():
    #Sat morning, Thursay Afternoon, Wed evening
    campaigns = ['camp_ins37_14347806900202', 'camp_ins37_14346230655561', 'camp_ins37_14345489653181']
    url1 = 'http://voiceapi.mvaayoo.com/voiceapi/CampaignReport?user=komalvis007g@gmail.com:babboo&campaign_id='
    url2 = '&start_date=2015-05-01&end_date=2015-12-31'
    rsp_sm = {}
    rsp_ta = {}
    rsp_we = {}
    
    status_map = {
        3:'Not Answered',
        4:'Answered',
        5:'Rejected',
        4096: 'DND'
    }

    response = requests.get(url1+campaigns[0]+url2).text
    rs = re.findall('1408973500[^<br>]*', response)
    rsp_sm = BuildCallMap(rs)

    response = requests.get(url1+campaigns[1]+url2).text
    rs = re.findall('1408973500[^<br>]*', response)
    rsp_ta = BuildCallMap(rs)

    response = requests.get(url1+campaigns[2]+url2).text
    rs = re.findall('1408973500[^<br>]*', response)
    rsp_we = BuildCallMap(rs)    

    print rsp_sm
    print rsp_ta
    print rsp_we

    f= open('IVRActivityReport_ANMs_Jhansi.txt', 'w')
    from mcts_identities.models import CareProvider, Beneficiary
    anms = CareProvider.objects.filter(designation='ANM')
    num_active_ans = 0
    num_active_total = 0
    num_dnd = 0
    import traceback, sys
    for anm in anms:
        try:
            block = Beneficiary.objects.all().filter(careprovider=anm)[0].subcenter.block
        except:
            traceback.print_exc(file=sys.stdout)
            continue
        status_sm = rsp_sm.get(anm.phone)
        status_ta = rsp_ta.get(anm.phone)
        status_we = rsp_we.get(anm.phone)
        is_active_ans = True if (status_sm == 4 or status_ta == 4 or status_we == 4) else False
        is_active_total = True if (is_active_ans or status_sm == 3 or status_ta == 3 or status_we == 3) else False
        is_dnd = True if status_we == 4096 else False
        num_dnd = num_dnd + 1 if is_dnd else num_dnd
        num_active_ans = num_active_ans + 1 if is_active_ans else num_active_ans
        num_active_total = num_active_total + 1 if is_active_total else num_active_total
        f.write("\n\n")
        f.write("NAME: "+anm.first_name+" "+anm.last_name+"\t")
        f.write("ROLE: "+anm.designation+"\t")
        f.write("BLOCK: "+block.name+"\t")
        f.write("PHONE: "+anm.phone+"\t")
        if is_dnd:
            f.write("DND: Yes\t")
        else:
            answered = "Yes" if is_active_ans else "No"
            active = "Yes" if is_active_total else "No"
            sm_we = status_map[status_we] if status_we else "NA"
            sm_ta = status_map[status_ta] if status_ta else "NA"
            sm_sm = status_map[status_sm] if status_sm else "NA"
            f.write("ANSWERED: "+answered+"\t")
            f.write("ACTIVE: "+active+"\n")
            f.write("Wednesday Evening(17/06): "+sm_we+"\n")
            f.write("Thursday Afternoon(18/06): "+sm_ta+"\n")
            f.write("Saturday Morning(20/06): "+sm_sm+"\n")
        f.write("\n================================================================================\n")
    f.write("\nTotal DND: "+str(num_dnd)+"\n")
    f.write("Total Answered: "+str(num_active_ans)+"\n")
    f.write("Total Active: "+str(num_active_total)+"\n")
    f.close()

def AddInitialUsers():
    from mcts_identities.models import CareProvider
    cp = CareProvider(designation='DOC', username="dpm_jhansi")
    cp.save()
    cp.set_password("doj_1602")
    cp.save()

    cp = CareProvider(designation='DOC', username='cmo_jhansi')
    cp.save()
    cp.set_password("coj_1602")
    cp.save()
    #cp.set_password("coj_1602")

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
    orm.SMSMessages.objects.create(msg_identifier="SMS_FAILURE",msg=u"एसएमएस का प्रारूप गलत है. एसएमएस नजरअंदाज कर दिया गया है.")
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
    TaskScheduler.schedule_every(task_name='sms.tasks.ReceiveSMSSinceLast', period='minutes', every='1')

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