# -*- coding: utf-8 -*-

import base64
import uuid
#from django.contrib.auth.models import User
from django.conf import settings
from datetime import date, datetime, time, timedelta
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
import xlsxwriter
from mcts_identities.models import IMMBenef, ANCBenef, Beneficiary, Block, SubCenter, Address, CareProvider
from mcts_transactions.models import DueEvents, OverDueEvents

def DumpSubCList():
    subcenters = SubCenter.objects.all()
    subs = []
    for subcenter in subcenters:
        sub_dict = {
            'type':'SubCenter'
        }
        sub_dict['name'] = subcenter.name
        sub_dict['MCTS_Id'] = subcenter.MCTS_ID
        subs.append(sub_dict)
    if subs:
        f = open('SunCenter_List.json', 'w')
        f.write(json.dumps(subs))
        f.close() 

def GenerateNumberString_ANM(benefs):
    due_anms = CareProvider.objects.filter(beneficiaries__in=benefs).distinct()
    number_string = ''
    for due_anm in due_anms:
        if number_string:
            number_string += ','
        number_string += '91'+due_anm.phone
    return number_string
    
def ANMIvrForOverdueServices(test=True):
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    from sms.sender import SendVoiceCall

    #Voice call for IMM due services
    imm_benefs = IMMBenef.objects.filter(odue_events__date=date_then).distinct()
    imm_voice_file = 'ANM_ODUE_IMM_REMINDER_20150703142712856239.wav'
    imm_number_string = GenerateNumberString_ANM(imm_benefs)
    print 'ANMs for IMM over due services'
    print imm_number_string
    if test:
        imm_number_string = '919390681183' 

    #Voice call for ANC
    anc_benefs = ANCBenef.objects.filter(odue_events__date=date_then).distinct()
    anc_number_string = GenerateNumberString_ANM(anc_benefs)
    anc_voice_file = 'ANM_ODUE_ANC_REMINDER_20150703142527385436.wav'
    print 'ANMs for ANC over due services'
    print anc_number_string
    if test:
        anc_number_string = '919390681183'
    
    try:
        SendVoiceCall(rec_num = imm_number_string, voice_file=imm_voice_file, campaign_name='ANM_ODS_IMM_'+str(date_then))
        SendVoiceCall(rec_num = anc_number_string, voice_file=anc_voice_file, campaign_name='ANM_ODS_ANC_'+str(date_then))
    except:
        # Put exception detail here
        sys.exc_info()[0]
        pass
    

def BenefIVRForDueServices(test=True):
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    from sms.sender import SendVoiceCall

    #IMM
    imm_benefs = IMMBenef.objects.filter(due_events__date=date_then).distinct()
    imm_benef_voice_file = ''
    imm_benef_number_string = ''
    for benef in imm_benefs:
        if imm_benef_number_string:
            imm_benef_number_string += ','
        imm_benef_number_string += benef.notify_number
    print 'IMM beneficiaries to be reminded for due services this month'
    print imm_benef_number_string

    #ANC
    anc_benefs = ANCBenef.objects.filter(due_events__date=date_then).distinct()
    anc_benef_voice_file = ''
    anc_benef_number_string = ''
    for benef in anc_benefs:
        if anc_benef_number_string:
            anc_benef_number_string += ','
        anc_benef_number_string += benef.notify_number
    print 'ANC beneficiaries to be reminded for due services this month'
    print anc_benef_number_string

    if test:
        imm_benef_number_string = anc_benef_number_string = '919390681183'

    print 'Sending voice calls'
    try:
        SendVoiceCall(rec_num = imm_benef_number_string, voice_file=imm_benef_voice_file, campaign_name='BENEF_ODS_IMM_'+str(date_then))
        SendVoiceCall(rec_num = anc_benef_number_string, voice_file=anc_benef_voice_file, campaign_name='BENEF_ODS_ANC_'+str(date_then))
    except:
        #Put exception detail here
        print sys.exc_info()[0]
        pass

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

def FindActiveFromIVR(campaigns=None):
    #Sat morning, Thursay Afternoon, Wed evening
    if not campaigns:
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

    # f= open('IVRActivityReport_ANMs_Jhansi.txt', 'w')
    
    workbook = xlsxwriter.Workbook('IVRActivityReport_ANMs_Jhansi.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'NAME')
    worksheet.write('B1', 'ROLE')
    worksheet.write('C1', 'BLOCK')
    worksheet.write('D1', 'PHONE')
    worksheet.write('E1', 'DND')
    worksheet.write('F1', 'ANSWERED')
    worksheet.write('G1', 'ACTIVE')
    worksheet.write('H1', 'Wed Eve(17/06)')
    worksheet.write('I1', 'Thur Aft(18/06)')
    worksheet.write('J1', 'Sat Mor(20/06)')
    from mcts_identities.models import CareProvider, Beneficiary
    anms = CareProvider.objects.filter(designation='ANM')
    num_active_ans = 0
    num_active_total = 0
    num_dnd = 0
    row = 1
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
        #Write txt file and excel file
        # f.write("\n\n")
        # f.write("NAME: "+anm.first_name+" "+anm.last_name+"\t")
        # f.write("ROLE: "+anm.designation+"\t")
        # f.write("BLOCK: "+block.name+"\t")
        # f.write("PHONE: "+anm.phone+"\t")
        row = row + 1
        worksheet.write('A'+str(row), anm.first_name+" "+anm.last_name)
        worksheet.write('B'+str(row), anm.designation)
        worksheet.write('C'+str(row), block.name)
        worksheet.write('D'+str(row), anm.phone)
    
        if is_dnd:
            # f.write("DND: Yes\t")
            worksheet.write('E'+str(row), 'Yes')
            worksheet.write('F'+str(row), 'N/A')
            worksheet.write('G'+str(row), 'N/A')
            worksheet.write('H'+str(row), 'N/A')
            worksheet.write('I'+str(row), 'N/A')
            worksheet.write('J'+str(row), 'N/A')
        else:
            answered = "Yes" if is_active_ans else "No"
            active = "Yes" if is_active_total else "No"
            sm_we = status_map[status_we] if status_we else "NA"
            sm_ta = status_map[status_ta] if status_ta else "NA"
            sm_sm = status_map[status_sm] if status_sm else "NA"
            # f.write("ANSWERED: "+answered+"\t")
            # f.write("ACTIVE: "+active+"\n")
            # f.write("Wednesday Evening(17/06): "+sm_we+"\n")
            # f.write("Thursday Afternoon(18/06): "+sm_ta+"\n")
            # f.write("Saturday Morning(20/06): "+sm_sm+"\n")
            worksheet.write('E'+str(row), 'NO')
            worksheet.write('F'+str(row), answered)
            worksheet.write('G'+str(row), active)
            worksheet.write('H'+str(row), sm_we)
            worksheet.write('I'+str(row), sm_ta)
            worksheet.write('J'+str(row), sm_sm)
    #     f.write("\n================================================================================\n")
    # f.write("\nTotal Numbers: "+str(anms.count())+"\n")
    # f.write("Total DND: "+str(num_dnd)+"\n")
    # f.write("Total Answered: "+str(num_active_ans)+"\n")
    # f.write("Total Active: "+str(num_active_total)+"\n")
    row = row+2
    worksheet.write('A'+str(row), 'Total Numbers')
    worksheet.write('B'+str(row), 'Total DND')
    worksheet.write('C'+str(row), 'Total Answered')
    worksheet.write('D'+str(row), 'Total Active')

    row = row + 1
    worksheet.write('A'+str(row), str(anms.count()))
    worksheet.write('B'+str(row), str(num_dnd))
    worksheet.write('C'+str(row), str(num_active_ans))
    worksheet.write('D'+str(row), str(num_active_total))

    # f.close()
    workbook.close()

def get_benef_counter(benef, date_then):
    benef_type = benef.get_type()
    date_then = date_then + timedelta(days=5)
    if benef_type == Beneficiary.ANC:
        ret = (1,0,0,0)
    elif benef_type == Beneficiary.IMM:
        imm_benef = benef.immbenef
        age = (date_then - imm_benef.dob).days
        if age <= 30:
            ret = (0,1,0,0)
        elif age <= 365:
            ret = (0, 0, 1, 0)
        elif age <=740:
            ret = (0,0,0,1)
    return ret

def generate_counts_per_village(benefs, date_then):
    anc_v2c_map = {}
    inf1_v2c_map = {}
    inf2_v2c_map = {}
    kid_v2c_map = {}

    for benef in benefs:
        village = benef.address.village
        if not anc_v2c_map.get(village):
            anc_v2c_map[village] = 0
        if not inf1_v2c_map.get(village):
            inf1_v2c_map[village] = 0
        if not inf2_v2c_map.get(village):
            inf2_v2c_map[village] = 0
        if not kid_v2c_map.get(village):
            kid_v2c_map[village] = 0

        benef_counter = get_benef_counter(benef, date_then) 
        anc_v2c_map[village] += benef_counter[0]
        inf1_v2c_map[village] += benef_counter[1]
        inf2_v2c_map[village] += benef_counter[2]
        kid_v2c_map[village] += benef_counter[3] 
    return (anc_v2c_map, inf1_v2c_map, inf2_v2c_map, kid_v2c_map)

def BeneficiariesPerVillage():
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz) 
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    # due_services_now = DueEvents.objects.filter(date = date_then)
    # odue_services_now = OverDueEvents.objects.filter(date = date_then)
    # benef_ids = []
    # print due_services_now.count()
    # print odue_services_now.count()
    # for dsn in due_services_now:
    #     if not dsn.beneficiary_id in benef_ids:
    #         benef_ids.append(dsn.beneficiary_id)
    # for osn in odue_services_now:
    #     if not osn.beneficiary_id in benef_ids:
    #         benef_ids.append(osn.beneficiary_id)
    
    benefs = Beneficiary.objects.all().filter(due_events__date=date_then).distinct() | Beneficiary.objects.filter(odue_events__date=date_then).distinct()
    
    print 'Obtained beneficiaries'
    block_ids = benefs.values('subcenter__block').distinct()
    print 'Obtained blocks'
    for block_id in block_ids:
        if block_id['subcenter__block']:
            block = Block.objects.get(id = block_id['subcenter__block'])
            benefs_block = benefs.filter(subcenter__block=block)
            print "Start HC generator, Block "+block.name
            anc_v2c_map, inf1_v2c_map, inf2_v2c_map, kid_v2c_map = generate_counts_per_village(benefs_block, date_then)
            print "End HC generator and start report generator, Block "+block.name
            workbook = xlsxwriter.Workbook('HeadCountFromWorkplan_'+block.name+'.xlsx')
            worksheet = workbook.add_worksheet()
            worksheet.write('A1', block.name)
            worksheet.write('A2', 'Serial')
            worksheet.write('B2', 'Village')
            worksheet.write('C2', 'Total Pregnant Ladies')
            worksheet.write('D2', 'Infants 0-1 month')
            worksheet.write('E2', 'Infants 1-12 months')
            worksheet.write('F2', 'Children 1-2 years')
            row = 2
            sum1 = sum2 = sum3 = sum4 = 0
            for village, value in anc_v2c_map.iteritems():
                row += 1
                worksheet.write('A'+str(row), str(row - 2))
                worksheet.write('B'+str(row), village)
                worksheet.write('C'+str(row), anc_v2c_map[village])
                worksheet.write('D'+str(row), inf1_v2c_map[village])
                worksheet.write('E'+str(row), inf2_v2c_map[village])
                worksheet.write('F'+str(row), kid_v2c_map[village])
                sum1 += anc_v2c_map[village]
                sum2 += inf1_v2c_map[village]
                sum3 += inf2_v2c_map[village]
                sum4 += kid_v2c_map[village]
            row += 1
            worksheet.write('B'+str(row), 'TOTAL')
            worksheet.write('C'+str(row), sum1)
            worksheet.write('D'+str(row), sum2)
            worksheet.write('E'+str(row), sum3)
            worksheet.write('F'+str(row), sum4)
            workbook.close()
            print 'Reporting done for block '+block.name

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

def CleanVillageNames():
    import jellyfish
    subcenters = SubCenter.objects.all()
    for subc in subcenters:
        villages = Address.objects.filter(beneficiaries__subcenter=subc).distinct()
        nl_vills = villages.filter(village_mcts_id = None) 
        l_vills = villages.exclude(village_mcts_id = None)
        phonetic_codes = []
        for l_vill in l_vills:
            phonetic_codes.append(jellyfish.nysiis(l_vill.village))
        #match the non-legitimate ones
        for nl_vill in nl_vills:
            pc = jellyfish.nysiis(nl_vill.village)
            min_dist = 100
            min_ind = 0
            ind = 0
            for spc in phonetic_codes:
                dist = jellyfish.jaro_distance(spc ,pc)
                if dist <= min_dist:
                    min_ind = ind
                    min_dist = dist
                ind +=1
            if min_dist < 1.0:
                match_vill = l_vills[min_ind]
                nl_vill.village_mcts_id = match_vill.village_mcts_id
                nl_vill.value = nl_vill.value+'_m'
                nl_vill.save()

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