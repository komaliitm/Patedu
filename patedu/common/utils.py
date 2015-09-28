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
from django.db.models import Q, Count, Max
import pytz
from schedule_api.models import TaskScheduler
import requests, re
import xlsxwriter
from common.models import ANCReportings, IMMReportings
from mcts_identities.models import IMMBenef, ANCBenef, Beneficiary, Block, SubCenter, Address,  CareProvider, CareGiver, HealthFacility, District
from mcts_transactions.models import DueEvents, OverDueEvents, Events
from sms.sender import SendSMSUnicode, connect_customer_to_app

def LoadLatLong():
    with open("sublatlong.json", 'r') as f:
        j_string = f.read()

    subcenters = json.loads(j_string)
    f.close()

    for subc in subcenters:
        try:
            sub = SubCenter.objects.get(MCTS_ID=subc["MCTS_Id"])
            print "Updating for "+sub.name
            sub._lat = subc["lat"]
            sub._long = subc["long"]
            sub.save()
        except:
            continue

def AccountsInit():
    blocks = Block.objects.all()
    for block in blocks:
        try:
            user = CareProvider.objects.create(username=block.name.replace(' ','_'), first_name=block.name, designation='DOC')
            user.set_password("abcd@1234")
            user.save()
            print "created user: "+block.name.replace(' ','_')
        except:
            pass

def LoadPopulationData(orm, year):
    file_to_read = 'population_data_'+str(year)+'.txt'
    file_path = os.path.join(settings.STATIC_ROOT, 'common', file_to_read)
    with open(file_path, 'r') as f:
        j_string = f.read()
    print j_string
    population_items = json.loads(j_string)
    from common.models import PopulationData
    for population_item in population_items:
        population_data = PopulationData.objects.create(population= population_item["population"], last_updated=utcnow_aware(),\
            MCTS_ID=population_item["MCTS_ID"], unit_type=population_item["unit_type"])

def LoadNHMTargets(orm, year):
    file_to_read = 'nhm_targets_'+str(year)+'.txt'
    file_path = os.path.join(settings.STATIC_ROOT, 'common', file_to_read)
    with open(file_path, 'r') as f:
        j_string = f.read()
    print j_string
    targets = json.loads(j_string)
    from common.models import NHMTargets
    for target in targets:
        district = District.objects.get(MCTS_ID = str(target["district"]))
        nhm_target = NHMTargets.objects.create(target_type=target["target_type"], target_year=int(target["target_year"]),\
         target_value=int(target["target_value"]), last_updated=utcnow_aware(), district=district)

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

def ServicesStringGenerator(qs, type):
    if type == 'ds':
        stats = 'Due Services: '
    else:
        stats = 'Overdue Services: '

    stats = ''
    for q in qs:
        event = Events.objects.get(id=q.get('event'))
        event_count = q.get('count')
        stats += event.val+' '+str(event_count)
        stats += ', '

    stats +='\n'
    return stats

def services_processor(benefs, type, mode=0):
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()

    services_string = ''
    ods = OverDueEvents.objects.filter(beneficiary__in=benefs, date=date_then)
    if mode:
        ods_services= ods.values('event').annotate(count=Count('event'))
        services_string += ServicesStringGenerator(ods_services, 'ods')
    count = ods.count()
    if type == 'ds':
        ds = DueEvents.objects.filter(beneficiary__in=benefs, date=date_then)
        count +=ds.count()
        if mode:
            ds_services = ds.values('event').annotate(count=Count('event'))
            services_string += ServicesStringGenerator(ds_services, 'ds')
    
    return count, services_string

def CallWrapper_Exotel(id, role, type, demo_phone=None):
    try:
        if role == 'ANM':
            anm = CareProvider.objects.get(id=int(id))
            phone = anm.phone
            benefs = Beneficiary.objects.filter(careprovider=anm)
            count, string = services_processor(benefs=benefs, type=type, mode=1)
        else:
            asha = CareGiver.objects.get(id=int(id))
            phone = asha.phone
            benefs = Beneficiary.objects.filter(caregiver=asha)
            count, string = services_processor(benefs=benefs, type=type, mode=1)
    except:
        print 'd'
        return 'ANM/ASHA does not exist'

    string = unicode(string)
    if len(string) > 20:
        string = string[0:20] + u"आदि " 
    sms_text = u"आपके क्षेत्र में शेष सर्विसेज- \n"+string+u"प्रेषक,\n मुख्य चिकित्साधिकारी, झाँसी"
    if demo_phone:
        phone = demo_phone
    #Send SMS
    sms_text_hexlified = toHex(sms_text)
    print sms_text_hexlified
    SendSMSUnicode(recNum=phone, msgtxt=sms_text_hexlified)
    #Send Exotel Call here
    # custom_field = str(id)+"_"+role+"_"+type
    # connect_customer_to_app(customer_no=phone, callerid="01130017630", CustomField=custom_field)

def GenerateNumberString_ANM(benefs):
    due_anms = CareProvider.objects.filter(beneficiaries__in=benefs).distinct()
    number_string = ''
    for due_anm in due_anms:
        if number_string:
            number_string += ','
        number_string += '91'+due_anm.phone
        CallWrapper_Exotel(due_anm.id, 'ANM', 'ods')
    number_string += ',919390681183'
    return number_string
    
def ANMIvrForOverdueServices_MVaayoo(test=True):
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    from sms.sender import SendVoiceCall

    #Voice call for IMM due services
    imm_benefs = IMMBenef.objects.filter(odue_events__date=date_then).distinct()
    imm_voice_file = 'Overdue_20150926130127834443.wav'
    imm_number_string = GenerateNumberString_ANM(imm_benefs)
    print 'ANMs for IMM over due services'
    print imm_number_string
    if test:
        imm_number_string = '919390681183' 

    #Voice call for ANC
    anc_benefs = ANCBenef.objects.filter(odue_events__date=date_then).distinct()
    anc_number_string = GenerateNumberString_ANM(anc_benefs)
    anc_voice_file = 'Overdue_20150926130127834443.wav'
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

def GenerateNumberString_ASHA(benefs):
    due_ashas = CareGiver.objects.filter(beneficiaries__in=benefs).distinct()
    number_string = ''
    for due_asha in due_ashas:
        if number_string:
            number_string += ','
        number_string += '91'+due_asha.phone
        CallWrapper_Exotel(due_asha.id, 'ASHA', 'ods')
    number_string += ',919390681183'
    return number_string
    
def IvrForWPServices_MVaayoo(test=True):
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    from sms.sender import SendVoiceCall

    #Voice Call for all overdue services
    benefs = Beneficiary.objects.filter(odue_events__date=date_then).distinct()
    voice_file = 'Overdue_20150926130127834443.wav'
    number_string_asha = GenerateNumberString_ASHA(benefs)
    number_string_annm = GenerateNumberString_ANM(benefs)
    print 'ASHAs, ANMs for IMM over due services'
    print number_string_asha
    print number_string_annm
    if test:
        number_string_asha = '919390681183, 919335237572'
        number_string_anm = '919390681183, 919335237572' 

    # #Voice call for IMM due services
    # imm_benefs = IMMBenef.objects.filter(odue_events__date=date_then).distinct()
    # imm_voice_file = 'Overdue_20150926130127834443.wav'
    # imm_number_string = GenerateNumberString_ASHA(imm_benefs)
    # print 'ASHAs for IMM over due services'
    # print imm_number_string
    # if test:
    #     imm_number_string = '919390681183' 

    # #Voice call for ANC
    # anc_benefs = ANCBenef.objects.filter(odue_events__date=date_then).distinct()
    # anc_number_string = GenerateNumberString_ANM(anc_benefs)
    # anc_voice_file = 'Overdue_20150926130127834443.wav'
    # print 'ASHAs for ANC over due services'
    # print anc_number_string
    # if test:
    #     anc_number_string = '919390681183'
    
    try:
        SendVoiceCall(rec_num = number_string_asha, voice_file=voice_file, campaign_name='ASHA_ODS_IMM_'+str(date_then))
        SendVoiceCall(rec_num = number_string_anm, voice_file=voice_file, campaign_name='ANM_ODS_ANC_'+str(date_then))
    except:
        # Put exception detail here
        sys.exc_info()[0]
        pass

def SaveANCBenef(benef):
    lmp_date = benef.get('LMP Date')
    if lmp_date:
        lmp_date = datetime.strptime(lmp_date, "%d/%m/%Y").date() 
    else:
        lmp_date = None
    edd = benef.get('Expected Date Of delivery')
    if edd:
        edd = datetime.strptime(edd, "%d/%m/%Y").date()
    else:
        edd = None

    husband_name = benef.get("Husband's Name").strip()
    mother_mcts_id = benef.get("Mother ID").strip()
    mother_name = benef.get('Mother Name').strip()
    notify_number = benef.get('Phone No.')
    notify_number_type = Beneficiary.NUMBER_TYPE.SELF
    subcenter_rs = benef.get('SubFacility / SubCentr')
    address  = benef.get(' Village')
    anm_phone  = benef.get('ANM Phone No.')
    anm_name = benef.get('ANM Name').strip()
    asha_phone = benef.get('ASHA Phone No.')
    asha_name = benef.get('ASHA Name').strip()
    benef_username = mother_mcts_id+'_'+mother_name
    benef_username = benef_username[-29:]
    district_rs = benef.get('Distric')
    block_rs = benef.get('Health Bloc')
    health_facility_rs = benef.get('Health Facilit')
    anc1_date = datetime.strptime(benef.get('ANC1 Date'), "%d/%m/%Y").date() if benef.get('ANC1 Date') else None
    anc2_date = datetime.strptime(benef.get('ANC2 Date'), "%d/%m/%Y").date() if benef.get('ANC2 Date') else None
    anc3_date = datetime.strptime(benef.get('ANC3 Date'), "%d/%m/%Y").date() if benef.get('ANC3 Date') else None
    anc4_date = datetime.strptime(benef.get('ANC4 Date'), "%d/%m/%Y").date() if benef.get('ANC4 Date') else None
    delivery_date = datetime.strptime(benef.get('Delivery/\nAbortion Date'), "%d/%m/%Y").date() if benef.get('Delivery/\nAbortion Date') else None
    
    anc_benef_qs = ANCBenef.objects.filter(MCTS_ID=mother_mcts_id)
    if anc_benef_qs:
        anc_benef = anc_benef_qs[0]
        if anc1_date or anc2_date or anc3_date or anc4_date or delivery_date:
            try:
                anc_reporting = ANCReportings.objects.get(benef=anc_benef)
            except:
                anc_reporting = ANCReportings.objects.create(benef=anc_benef)
            anc_reporting.anc1_date = anc1_date
            anc_reporting.anc2_date = anc2_date
            anc_reporting.anc3_date = anc3_date
            anc_reporting.anc4_date = anc4_date
            anc_reporting.delivery_date = delivery_date
            anc_reporting.save()
            print 'ANC benef services added'
        print 'ANC Benef Already exists'
        return

    t_district = []
    if district_rs:
        district_rs = district_rs.lower()
        _regSearch = re.search('([a-z ]+)', district_rs)
        if _regSearch:
            district_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', district_rs)
        if _regSearch:
            district_id = _regSearch.group(0).strip()
        #Hardcoding
        district_id = '36'
        if district_id and district_name:
            t_district = [district_name, district_id]
    
    t_block = []
    if block_rs:
        block_rs = block_rs.lower()
        _regSearch = re.search('([a-z ]+)', block_rs)
        if _regSearch:
            block_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', block_rs)
        if _regSearch:
            block_id = _regSearch.group(0).strip()
        if block_id and block_name:
            t_block = [block_name, block_id]

    t_health_facility = []
    if health_facility_rs:
        health_facility_rs = health_facility_rs.lower()
        _regSearch = re.search('([a-z ]+)', health_facility_rs)
        if _regSearch:
            health_facility_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', health_facility_rs)
        if _regSearch:
            health_facility_id = _regSearch.group(0).strip()
        if health_facility_name and health_facility_id:
            t_health_facility = [health_facility_name, health_facility_id]

    #check and create district
    if t_district:
        dsts = District.objects.filter(MCTS_ID = t_district[1])
        if dsts:
            district = dsts[0]
        else:
            district = District.objects.create(MCTS_ID = t_district[1], name=t_district[0])
    else:
        district = None

    #check and create block
    if t_block:
        blocks = Block.objects.filter(MCTS_ID = t_block[1])
        if blocks:
            block = blocks[0]
        else:
            block = Block.objects.create(MCTS_ID = t_block[1], name=t_block[0])
    else:
        block = None

    #check and create health facility
    if t_health_facility:
        hfs = HealthFacility.objects.filter(MCTS_ID = t_health_facility[1])
        if hfs:
            health_facility = hfs[0]
        else:
            health_facility = HealthFacility.objects.create(MCTS_ID = t_health_facility[1], name = t_health_facility[0])
    else:
        health_facility = None

    #process subcenter
    subcenter = None
    if subcenter_rs:
        subcenter_rs = subcenter_rs.replace("\n","").lower().strip()
        _regSearch = re.search('(\d+)',subcenter_rs)
        if _regSearch:
            subc_id = _regSearch.group(0)
            existing_subc = SubCenter.objects.filter(MCTS_ID=subc_id)
            if existing_subc:
                subcenter = existing_subc[0]
            else:
                _regSearch = re.search('([a-z ]+)',subcenter_rs)
                if _regSearch:
                    subc_name = _regSearch.group(0).strip()
                else:
                    subc_name = subc_id
                subcenter = SubCenter.objects.create(MCTS_ID = subc_id, name=subc_name, district=district, block=block, health_facility=health_facility)

    #Process address
    vill_name = None
    vill_mcts_id = None
    vill_value = None
    if address:
        address = address.replace("\n", "").lower()
        vill_value = address
        _regSearch = re.search('([a-z ]+)', address)
        if _regSearch:
            vill_name = _regSearch.group(0).strip()
        _regSearch = re.search('(\d+)', address)
        if _regSearch:
            vill_mcts_id = _regSearch.group(0)
    #check and create address
    addrs = None
    if vill_mcts_id is not None:
        addrs = Address.objects.filter(village_mcts_id=vill_mcts_id)
    if not addrs and vill_value is not None:
        addrs = Address.objects.filter(value=vill_value)
    if addrs:
        village = addrs[0]
    else: 
        try:
            village = Address.objects.create(value=vill_value, village=vill_name, village_mcts_id = vill_mcts_id)
        except:
            village = None

    #process caregiver
    if asha_name:
        cgs = CareGiver.objects.filter(designation='ASHA', phone=asha_phone)
        if cgs:
            cg = cgs[0]
            if cg.first_name != asha_name:
                cg.first_name = asha_name
                cg.save()
        else:
            username = asha_name+"_"+asha_phone+"_ASHA"
            username = username[0:29]
            cg = CareGiver.objects.create(first_name=asha_name, designation='ASHA', phone=asha_phone, address=village, username=username)
    else:
        cg = None

    #process careprovider
    if anm_name:
        cps = CareProvider.objects.filter(designation='ANM', phone=anm_phone)
        if cps:
            cp = cps[0]
            if cp.first_name != anm_name:
                cp.first_name = anm_name
                cp.save()
        else:
            username = anm_name +"_"+anm_phone+"_ANM"
            username = username[0:29]
            cp = CareProvider.objects.create(first_name=anm_name, designation='ANM', phone=anm_phone, username=username, address=village)
    else:
        cp = None

    print benef_username
    anc_benef = ANCBenef.objects.create(LMP= lmp_date, EDD= edd, husband= husband_name, \
        active=True, MCTS_ID=mother_mcts_id, notify_number=notify_number, notify_number_type= notify_number_type, \
        address=village, createdon=utcnow_aware(), modifiedon=utcnow_aware(), subcenter=subcenter, \
        first_name=mother_name, caregiver=cg, careprovider=cp, username=benef_username)
    if anc1_date or anc2_date or anc3_date or anc4_date or delivery_date:
        anc_reporting = ANCReportings.objects.create(benef=anc_benef)
        anc_reporting.anc1_date = anc1_date
        anc_reporting.anc2_date = anc2_date
        anc_reporting.anc3_date = anc3_date
        anc_reporting.anc4_date = anc4_date
        anc_reporting.delivery_date = delivery_date
        anc_reporting.save()

def SaveIMMBenef(benef):
    birthdate = benef.get('Date of Birth')
    if birthdate:
        birthdate = datetime.strptime(birthdate, "%d/%m/%Y").date()
    else:
        birthdate = None

    child_name = benef.get('Child Name')
    child_sex = benef.get('Sex')
    mother_name = benef.get("Mother's Name")
    mother_mcts_id = benef.get('Mother ID')
    child_mcts_id = benef.get('Child ID').strip()
    notify_number = benef.get('Phone No.')
    notify_number_type = Beneficiary.NUMBER_TYPE.SELF
    subcenter_rs = benef.get('SubFacility / SubCentr')
    address  = benef.get(' Village')
    anm_phone  = benef.get('ANM Phone No.')
    anm_name = benef.get('ANM Name').strip()
    asha_phone = benef.get('ASHA Phone No.')
    asha_name = benef.get('ASHA Name').strip()
    benef_username = child_mcts_id+'_'+child_name
    benef_username = benef_username[-29:]
    district_rs = benef.get('Distric')
    block_rs = benef.get('Health Bloc')
    health_facility_rs = benef.get('Health Facilit')
    measles_date = benef.get('Measles Date')
    if measles_date:
        measles_date = datetime.strptime(measles_date, "%d/%m/%Y").date()
    else:
        measles_date = None    

    imm_benef_qs = IMMBenef.objects.filter(MCTS_ID=child_mcts_id)
    if imm_benef_qs:
        imm_benef = imm_benef_qs[0]
        if measles_date:
            try:
                imm_reporting = IMMReportings.objects.get(benef=imm_benef)
            except:
                imm_reporting = IMMReportings.objects.create(benef=imm_benef)
            imm_reporting.measles_date = measles_date
            imm_reporting.save()
            print 'IMM benef services added'

        print 'IMM Benef already exists'
        return

    t_district = []
    if district_rs:
        district_rs = district_rs.lower()
        _regSearch = re.search('([a-z ]+)', district_rs)
        if _regSearch:
            district_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', district_rs)
        if _regSearch:
            district_id = _regSearch.group(0).strip()
        #Hardcoding
        district_id = '36'
        if district_id and district_name:
            t_district = [district_name, district_id]
    
    t_block = []
    if block_rs:
        block_rs = block_rs.lower()
        _regSearch = re.search('([a-z ]+)', block_rs)
        if _regSearch:
            block_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', block_rs)
        if _regSearch:
            block_id = _regSearch.group(0).strip()
        if block_id and block_name:
            t_block = [block_name, block_id]

    t_health_facility = []
    if health_facility_rs:
        health_facility_rs = health_facility_rs.lower()
        _regSearch = re.search('([a-z ]+)', health_facility_rs)
        if _regSearch:
            health_facility_name = _regSearch.group(0).strip()
        _regSearch= re.search('(\d+)', health_facility_rs)
        if _regSearch:
            health_facility_id = _regSearch.group(0).strip()
        if health_facility_name and health_facility_id:
            t_health_facility = [health_facility_name, health_facility_id]

    #check and create district
    if t_district:
        dsts = District.objects.filter(MCTS_ID = t_district[1])
        if dsts:
            district = dsts[0]
        else:
            district = District.objects.create(MCTS_ID = t_district[1], name=t_district[0])
    else:
        district = None

    #check and create block
    if t_block:
        blocks = Block.objects.filter(MCTS_ID = t_block[1])
        if blocks:
            block = blocks[0]
        else:
            block = Block.objects.create(MCTS_ID = t_block[1], name=t_block[0])
    else:
        block = None

    #check and create health facility
    if t_health_facility:
        hfs = HealthFacility.objects.filter(MCTS_ID = t_health_facility[1])
        if hfs:
            health_facility = hfs[0]
        else:
            health_facility = HealthFacility.objects.create(MCTS_ID = t_health_facility[1], name = t_health_facility[0])
    else:
        health_facility = None

    #process subcenter
    subcenter = None
    if subcenter_rs:
        subcenter_rs = subcenter_rs.replace("\n","").lower().strip()
        _regSearch = re.search('(\d+)',subcenter_rs)
        if _regSearch:
            subc_id = _regSearch.group(0)
            existing_subc = SubCenter.objects.filter(MCTS_ID=subc_id)
            if existing_subc:
                subcenter = existing_subc[0]
            else:
                _regSearch = re.search('([a-z ]+)',subcenter_rs)
                if _regSearch:
                    subc_name = _regSearch.group(0).strip()
                else:
                    subc_name = subc_id
                subcenter = SubCenter.objects.create(MCTS_ID = subc_id, name=subc_name, district=district, block=block, health_facility=health_facility)

    #Process address
    vill_name = None
    vill_mcts_id = None
    vill_value = None
    if address:
        address = address.replace("\n", "").lower()
        vill_value = address
        _regSearch = re.search('([a-z ]+)', address)
        if _regSearch:
            vill_name = _regSearch.group(0).strip()
        _regSearch = re.search('(\d+)', address)
        if _regSearch:
            vill_mcts_id = _regSearch.group(0)
    #check and create address
    addrs = None
    if vill_mcts_id is not None:
        addrs = Address.objects.filter(village_mcts_id=vill_mcts_id)
    if not addrs and vill_value is not None:
        addrs = Address.objects.filter(value=vill_value)
    if addrs:
        village = addrs[0]
    else: 
        try:
            village = Address.objects.create(value=vill_value, village=vill_name, village_mcts_id = vill_mcts_id)
        except:
            village = None

    #process caregiver
    if asha_name:
        cgs = CareGiver.objects.filter(designation='ASHA', phone=asha_phone)
        if cgs:
            cg = cgs[0]
            if cg.first_name != asha_name:
                cg.first_name = asha_name
                cg.save()
        else:
            username = asha_name+"_"+asha_phone+"_ASHA"
            username = username[0:29]
            cg = CareGiver.objects.create(first_name=asha_name, designation='ASHA', phone=asha_phone, address=village, username=username)
    else:
        cg = None

    #process careprovider
    if anm_name:
        cps = CareProvider.objects.filter(designation='ANM', phone=anm_phone)
        if cps:
            cp = cps[0]
            if cp.first_name != anm_name:
                cp.first_name = anm_name
                cp.save()
        else:
            username = anm_name +"_"+anm_phone+"_ANM"
            username = username[0:29]
            cp = CareProvider.objects.create(first_name=anm_name, designation='ANM', phone=anm_phone, username=username, address=village)
    else:
        cp = None

    print benef_username
    imm_benef = IMMBenef.objects.create(dob = birthdate, child_name=child_name, child_sex=child_sex, \
    mother_name=mother_name, mother_mcts_id= mother_mcts_id, active=True, MCTS_ID=child_mcts_id, \
    notify_number=notify_number, notify_number_type= notify_number_type, address=village, \
    createdon=utcnow_aware(), modifiedon=utcnow_aware(), subcenter=subcenter, \
    first_name=child_name, caregiver=cg, careprovider=cp, username=benef_username)

    if measles_date:
        imm_reporting = IMMReportings.objects.create(benef=imm_benef)
        imm_reporting.measles_date = measles_date
        imm_reporting.save()

def LoadBenefsFromJson(json_data_file, Type=ANCBenef):
    with open(json_data_file, 'r') as f:
        j_string = f.read()
    
    benefs = json.loads(j_string)
    print len(benefs)
    i = 0
    for benef in benefs:
        if Type == ANCBenef:
            SaveANCBenef(benef)
        elif Type == IMMBenef:
            SaveIMMBenef(benef)
        i +=1

def ANMIvrForOverdueServices_Exotel(mode=1, target=1):
    #mode = 1 Due
    #mode = 2 OverDue
    #mode = 3 Both
    if target == 1:
        benef_type = ANCBenef
    elif target == 2:
        benef_type = IMMBenef

    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)
    today = utcnow_aware().replace(tzinfo=tz)
    date_then = today.replace(hour=12, minute=0, day=1, second=0).date()
    from sms.sender import SendVoiceCall

    #Voice call for ANC
    if mode == 1:
        benefs = benef_type.objects.filter(due_events__date=date_then).distinct()
    elif mode ==2:
        benefs = benef_type.objects.filter(odue_events__date=date_then).distinct()
    else:
        abenefs = benef_type.objects.filter(odue_events__date=date_then).distinct() & ANCBenef.objects.filter(due_events__date=date_then).distinct()
    anms = CareProvider.objects.filter(beneficiaries__in=benefs).distinct()
    
    callerid = ""
    app_url = settings.EXOTEL_APP_URL
    for anm in amns:
        try:
            connect_customer_to_app(customer_no=due_anms.notify_number, callerid=callerid, app_url=app_url)
        except:
            sys.exec_info()[0]


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