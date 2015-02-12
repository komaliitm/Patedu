import json
import pytz
from django.http import HttpResponse
from django.template import Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from .forms import Document
from .models import Document, AvailableMCTSData, LatLangData
from mcts_transactions.models import *
from mcts_identities import * 

# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django import forms
import xlrd
import datetime
import re
from django.db.models import Q
from common.utils import utcnow_aware
        

    
list_header =     ['State' , 'District' , 'District_ID' , 'Health Block','Health_Block_ID' ,'Health Facility' ,'Health_Facility_ID', 'SubFacility / SubCentre','Village','ANM :' , 'ReportMonth', 'ReportYear']
list_header_key = ['State' , 'District' , 'District_ID' , 'Health_Block','Health_Block_ID', 'Health_Facility' ,'Health_Facility_ID', 'SubFacility','SubFacilityID','Village','ANM :' , 'ReportMonth', 'ReportYear']
                                                                                                                                                                              
list_columns_value = ['(Year of registration)\nMother ID' , 'Address(GP Village)' ,'Phone No. of(Phone No.)','Phone No. of(Phone No.)' ,'Phone No. of(Phone No. )' , 'Phone No. of (Phone No. )', 'LMP Date','Overdue Services','OverDue Services', 'Due Services' , 'Mother Name(w/o Husband Name)', 'Given Services' , 'Expected Delivery Date', 'Delivery Type', 'Delivery Date', 'Place Of Delivery' , 'Child Name (Sex )' , 'Mother Name( Mother ID )' , '(Year of registration)\nChild ID', 'Birthdate']
list_columns_key =   ['year_of_reg_mother_id' , 'address' ,'phone_no_of_whom','phone_no_of_whom', 'phone_no_of_whom' ,'phone_no_of_whom' ,'lmp_date','overDue_services','overDue_services', 'due_services' ,'mother_name_husband_name', 'given_services' ,'expected_delivery_date', 'delivery_type' , 'delivery_date' , 'place_of_delivery' , 'child_name_sex' , 'mother_name_mother_id' , 'year_of_reg_child_id' , 'birthdate']



def MctsPage(request):
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'sample.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )


def UploadPage(request):
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'myapp/list.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )

def uploadLangLatpage(request):
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'myapp/langlat.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )

def getStartingRow(sheet, initialIndex):
    k=initialIndex
    x=initialIndex
    y=0
    limitFlag = 0
    try:

        while sheet.cell_value(x,y) != "S.No" and limitFlag<20:
           
            x=x+1
            k=k+1
            limitFlag= limitFlag+1
        if limitFlag >= 20:
            return "NoData"
        else:
            return k
    except:
        print "Exception = getStartingRow"
        return "NoData"



colIndexes = []

def getColumnNames(sheet, startIndex):
    del colIndexes[:]
    x = startIndex
    y = 0
    colCount=0
    blankCount = 0
    columnArray = []
    if sheet.cell_value(x,y) == "S.No":
        while blankCount < 20  :
            try:
                if sheet.cell_value(x,y) == "":
                    blankCount = blankCount+1
                else:
                    #print "y="+str(y)

                    blankCount = 0
                    colIndexes.append(y)
                    tempColValue = sheet.cell_value(x,y)
                    for colValue in list_columns_value:
                      
                        if sheet.cell_value(x,y) == colValue:
                            tempColValue = list_columns_key[list_columns_value.index(colValue)]
                           

                    columnArray.append(tempColValue )
                    colCount = colCount+1
                y= y+1
            except Exception as e:
                print "Exception"
                print str(e)
                break
    #print "colIndexes1="+str(colIndexes)
               
    return columnArray

def getRowDict(rowIndex, columnArray, sheet ):
    dict_cell_value = {}
    y=0
    x = rowIndex
    
    while y < len(columnArray) :
        #print "col columnArray="+str(columnArray[y])
        #print "col index="+str(colIndexes[y])
        #print "rowval="+str(sheet.cell_value(x,colIndexes[y]))

        dict_cell_value[columnArray[y]] = sheet.cell_value(x,colIndexes[y])
        y=y+1
    return dict_cell_value       



def getHeaderDict(sheet, initialIndex, startIndex): 
    dict_header = {}
    while int(initialIndex) < int(startIndex):

        initialIndex=initialIndex+1
        cells = sheet.row_slice(rowx=initialIndex,start_colx=0,end_colx=25)

        for cell in cells:
            if  str(cell.value).find(list_header[0]) >= 0  :
                dict_header[list_header_key[0]] = cell.value.replace(' ' , '', 2).split(":")[1]
            else:
                if  str(cell.value).find(list_header[1]) >= 0  :
                    dict_header[list_header_key[1]] = cell.value.replace(' ' , '', 2).split(":")[1]
                else:
                    if str(cell.value).find(list_header[3]) >= 0  :
                        dict_header[list_header_key[3]] = cell.value.replace(' ' , '', 2).split(":")[1]
                    else:
                        if str(cell.value).find(list_header[5]) >= 0  :
                            dict_header[list_header_key[5]] = cell.value.replace(' ' , '', 2).split(":")[1]
                        else:
                            if str(cell.value).find(list_header[7]) >= 0  :
                                dict_header[list_header_key[7]] = cell.value.replace(' ' , '', 2).split(":")[1].split("(")[0]
                                dict_header[list_header_key[8]] = cell.value.replace(' ' , '', 2).split(":")[1].split("(")[1].split(")")[0]
                            else:
                                if str(cell.value).find("JAN") >= 0 or str(cell.value).find("FEB")>= 0  or str(cell.value).find("MAR")>= 0  or str(cell.value).find("APR")>= 0  or str(cell.value).find("MAY")>= 0  or str(cell.value).find("JUN")>= 0 or str(cell.value).find("JUL")>= 0  or str(cell.value).find("AUG")>= 0  or str(cell.value).find("SEP")>= 0  or str(cell.value).find("OCT")>= 0  or str(cell.value).find("NOV")>= 0  or str(cell.value).find("DEC")>= 0  :
                                    dict_header[list_header_key[11]] = cell.value.replace(' ' , '').split(",")[0]
                                    dict_header[list_header_key[12]] = cell.value.replace(' ' , '').split(",")[1]
    return dict_header


def mother_name_husband_name(benef, subcenter):
    expected_delivery_date = benef.get("expected_delivery_date")
    address = benef.get("address")
    phone_no_of_whom = benef.get("phone_no_of_whom")
    year_of_reg_mother_id = benef.get("year_of_reg_mother_id")
    delivery_date = benef.get("delivery_date")
    pnc_complications = benef.get("PNC Complication")
    asha_phone_name = benef.get("ASHA (Phone No.)")
    anm_phone_name = benef.get("ANM (Phone No.)")
    mother_name_husband_name = benef.get("mother_name_husband_name")
    lmp_date = benef.get("lmp_date")
    place_of_delivery = benef.get("place_of_delivery")
    delivery_type = benef.get("delivery_type")

    #parse lmp_date
    if lmp_date:
        lmp_date = datetime.datetime.strptime(lmp_date, "%d/%m/%Y").date()
    else:
        lmp_date = None

    #parse place_of_delivery
    if not place_of_delivery:
        place_of_delivery = None

    #parse delivery_type
    if not delivery_type:
        delivery_type = None

    #parse mother name husband name
    mother_name  = None
    husband_name = None
    if mother_name_husband_name:
        couple = mother_name_husband_name.lower().replace('\n', '').split('w/o')
        
        _regSearch = re.search('[a-z ]+', couple[0])
        if _regSearch:
            mother_name = _regSearch.group(0).strip()

        if len(couple) > 1:
            _regSearch = re.search('[a-z ]+', couple[1])
            if _regSearch:
                husband_name = _regSearch.group(0).strip()


    #parse delivery date
    edd = None
    if expected_delivery_date:
        edd = datetime.datetime.strptime(expected_delivery_date, "%d/%m/%Y").date()
    
    #parse village
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
    
    phone = None
    phone_type = None
    if phone_no_of_whom:
        raw_phone = phone_no_of_whom.replace("\n","").lower()

        _regSearch = re.search('(\d+)', raw_phone)
        if _regSearch:
            phone = _regSearch.group(0)

        _regSearch = re.search('([a-z]+)', raw_phone)
        if _regSearch:
            phone_type_str = _regSearch.group(0).lower()
            phone_type = Beneficiary.NUMBER_TYPE_MAP.get(phone_type_str)
            if phone_type is None:
                phone_type = 0

    #parse mother mcts id
    mother_mcts_id = None
    if year_of_reg_mother_id:
        mother_mcts_id = year_of_reg_mother_id.replace(" ","").replace("\n","").replace("(","").replace(")","_").replace("-","_")

    #parse delivery date
    dd = None
    if delivery_date:
        dd = datetime.datetime.strptime(delivery_date, "%d/%m/%Y").date()

    #parse pnc_complications
    if not pnc_complications:
        pnc_complications = None

    #parse ASHA phone, name
    asha_name = None
    asha_phone = None
    if asha_phone_name:
        asha_phone_name = asha_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', asha_phone_name)
        if _regSearch:
            asha_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', asha_phone_name)
        if _regSearch:
            asha_name = _regSearch.group(0).strip()

    #parse anm phone, name
    anm_name = None
    anm_phone = None
    if anm_phone_name:
        anm_phone_name = anm_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', anm_phone_name)
        if _regSearch:
            anm_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', anm_phone_name)
        if _regSearch:
            anm_name = _regSearch.group(0).strip()

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

    #check and create care giver
    if asha_name:
        cgs = CareGiver.objects.filter(first_name=asha_name, designation='ASHA', phone=asha_phone)
        if cgs.count() > 0:
            cg = cgs[0]
        else:
            username = asha_name+"_"+asha_phone+"_ASHA"
            username = username[0:29]
            cg = CareGiver.objects.create(first_name=asha_name, designation='ASHA', phone=asha_phone, address=village, username=username)
    else:
        cg = None

    #check and create care provider
    if anm_name:
        cps = CareProvider.objects.filter(first_name=anm_name, designation='ANM', phone=anm_phone)
        if cps.count() > 0:
            cp = cps[0]
        else:
            username = anm_name +"_"+anm_phone+"_ANM"
            username = username[0:29]
            cp = CareProvider.objects.create(first_name=anm_name, designation='ANM', phone=anm_phone, username=username)
    else:
        cp = None


    #check and create PNC benefeciary
    pnc_benefs = PNCBenef.objects.filter(MCTS_ID = mother_mcts_id)
    if pnc_benefs.count() > 0:
        pnc_benef = pnc_benefs[0]
    else:
        username = mother_mcts_id+"_"+mother_name
        pnc_benef = PNCBenef.objects.create(LMP= lmp_date, EDD= edd, husband= husband_name, ADD = dd, \
        delivery_place = place_of_delivery, delivery_type=delivery_type, \
        complications=pnc_complications, active=True, MCTS_ID=mother_mcts_id, \
        notify_number=phone, notify_number_type= phone_type, address=village, \
        createdon=utcnow_aware(), modifiedon=utcnow_aware(), subcenter=subcenter, \
        first_name=mother_name, caregiver=cg, careprovider=cp, username=username)


def SaveANCBeneficiary(benef, subcenter, date_then):
    print "In ANC Parser"
    expected_delivery_date = benef.get("expected_delivery_date")
    address = benef.get("address")
    phone_no_of_whom = benef.get("phone_no_of_whom")
    year_of_reg_mother_id = benef.get("year_of_reg_mother_id")
    asha_phone_name = benef.get("ASHA (Phone No.)")
    anm_phone_name = benef.get("ANM (Phone No.)")
    mother_name_husband_name = benef.get("mother_name_husband_name")
    lmp_date = benef.get("lmp_date")
    overDue_services = benef.get("overDue_services")
    given_services = benef.get("given_services")
    due_services = benef.get("due_services")
    
    #parse overdue services
    od_services = []
    if overDue_services:
        overDue_services = overDue_services.replace("\n","").lower()
        od_services = overDue_services.split(",")

    gn_services = []
    if given_services:
        given_services = given_services.replace("\n","").lower()
        gn_services = given_services.split(",")

    d_services = []
    if due_services:
        due_services = due_services.replace("\n", "").lower()
        d_services = due_services.split(",")

    #parse lmp_date
    if lmp_date:
        lmp_date = datetime.datetime.strptime(lmp_date, "%d/%m/%Y").date()
    else:
        lmp_date = None

    #parse mother name husband name
    mother_name  = None
    husband_name = None
    if mother_name_husband_name:
        couple = mother_name_husband_name.lower().replace('\n', '').split('w/o')
        
        _regSearch = re.search('[a-z ]+', couple[0])
        if _regSearch:
            mother_name = _regSearch.group(0).strip()

        if len(couple) > 1:
            _regSearch = re.search('[a-z ]+', couple[1])
            if _regSearch:
                husband_name = _regSearch.group(0).strip()

    #parse expected delivery date
    edd = None
    if expected_delivery_date:
        edd = datetime.datetime.strptime(expected_delivery_date, "%d/%m/%Y").date()
    
    #parse village
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
    
    #parse phone
    phone = None
    phone_type = None
    if phone_no_of_whom:
        raw_phone = phone_no_of_whom.replace("\n","").lower()

        _regSearch = re.search('(\d+)', raw_phone)
        if _regSearch:
            phone = _regSearch.group(0)

        _regSearch = re.search('([a-z]+)', raw_phone)
        if _regSearch:
            phone_type_str = _regSearch.group(0).lower()
            phone_type = Beneficiary.NUMBER_TYPE_MAP.get(phone_type_str)
            if phone_type is None:
                phone_type = 0

    #parse mother mcts id
    mother_mcts_id = None
    if year_of_reg_mother_id:
        mother_mcts_id = year_of_reg_mother_id.replace(" ","").replace("\n","").replace("(","").replace(")","_").replace("-","_")

    #parse ASHA phone, name
    asha_name = None
    asha_phone = ''
    if asha_phone_name:
        asha_phone_name = asha_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', asha_phone_name)
        if _regSearch:
            asha_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', asha_phone_name)
        if _regSearch:
            asha_name = _regSearch.group(0).strip()

    #parse anm phone, name
    anm_name = None
    anm_phone = ''
    if anm_phone_name:
        anm_phone_name = anm_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', anm_phone_name)
        if _regSearch:
            anm_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', anm_phone_name)
        if _regSearch:
            anm_name = _regSearch.group(0).strip()

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

    #check and create care giver
    if asha_name:
        cgs = CareGiver.objects.filter(first_name=asha_name, designation='ASHA', phone=asha_phone)
        if cgs.count() > 0:
            cg = cgs[0]
        else:
            username = asha_name+"_"+asha_phone+"_ASHA"
            username = username[0:29]
            cg = CareGiver.objects.create(first_name=asha_name, designation='ASHA', phone=asha_phone, address=village, username=username)
    else:
        cg = None

    #check and create care provider
    if anm_name:
        cps = CareProvider.objects.filter(first_name=anm_name, designation='ANM', phone=anm_phone)
        if cps.count() > 0:
            cp = cps[0]
        else:
            username = anm_name +"_"+anm_phone+"_ANM"
            username = username[0:29]
            cp = CareProvider.objects.create(first_name=anm_name, designation='ANM', phone=anm_phone, username=username)
    else:
        cp = None


    #check and create ANC benefeciary
    anc_benefs = ANCBenef.objects.filter(MCTS_ID = mother_mcts_id)
    if anc_benefs.count() > 0:
        anc_benef = anc_benefs[0]
        print 'benefeciary exists'
    else:
        username = mother_mcts_id+"_"+mother_name
        username = username[0:29]
        anc_benef = ANCBenef.objects.create(LMP= lmp_date, EDD= edd, husband= husband_name, \
        active=True, MCTS_ID=mother_mcts_id, \
        notify_number=phone, notify_number_type= phone_type, address=village, \
        createdon=utcnow_aware(), modifiedon=utcnow_aware(), subcenter=subcenter, \
        first_name=mother_name, caregiver=cg, careprovider=cp, username=username)
        #create beneficiary registration transaction
        events = Events.objects.filter(val=Events.ANC_REG_VAL)
        if events.count() > 0:
            event = events[0]
        else:
            event = Events.objects.create(val=Events.ANC_REG_VAL)
        
        try:
            Transactions.objects.create(event=event, subcenter=subcenter, beneficiary= anc_benef, timestamp=date_then)
        except:
            print "Tried to create anc_reg Transactions without benefeciary"


    #check and create events
    for service in d_services + od_services + gn_services:
        service = service.strip()
        scs = Events.objects.filter(val=service)
        if scs.count() == 0:
            event = Events.objects.create(val=service)

    #create DueEvents
    for service in d_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        des = DueEvents.objects.all().filter(event=event, subcenter=subcenter, beneficiary=anc_benef, date__month=date_then.month, date__year=date_then.year)
        if des:
            print 'DueEvent exists'
            continue
        try:
            DueEvents.objects.create(event=event, subcenter=subcenter, beneficiary= anc_benef, date=date_then)
        except:
            print "Tried to create DueEvents without benefeciary"
    #create over due events
    for service in od_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        odes = OverDueEvents.objects.all().filter(event=event, subcenter=subcenter, beneficiary=anc_benef, date__month=date_then.month, date__year=date_then.year)
        if odes:
            print 'Overdue event exists'
            continue
        try:
            OverDueEvents.objects.create(event=event, subcenter=subcenter, beneficiary= anc_benef, date=date_then)
        except:
            print "Tried to create OverDueEvents without benefeciary"
    #check and create Transactions
    for service in gn_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        dt_then = datetime.datetime.combine(date_then, datetime.datetime.min.time()) +  datetime.timedelta(days=1)
        dt_cutoff = utcnow_aware() - datetime.timedelta(days=ANCBenef.ANC_SPAN)
        txs = Transactions.objects.filter(beneficiary=anc_benef, event=event, timestamp__gt = dt_cutoff)
        if txs.count() > 0:
            print 'Transaction exists'
            continue
        try:
            Transactions.objects.create(event=event, subcenter=subcenter, beneficiary= anc_benef, timestamp=date_then)
        except:
            print "Tried to create Transactions without benefeciary"
    

def SaveIMMBeneficiary(benef, subcenter, date_then):
    address = benef.get("address")
    phone_no_of_whom = benef.get("phone_no_of_whom")
    year_of_reg_child_id = benef.get("year_of_reg_child_id")
    asha_phone_name = benef.get("ASHA (Phone No.)")
    anm_phone_name = benef.get("HealthProvider (Phone No.)")
    mother_name_mother_id = benef.get("mother_name_mother_id")
    birthdate = benef.get("birthdate")
    overDue_services = benef.get("overDue_services")
    given_services = benef.get("given_services")
    due_services = benef.get("due_services")
    child_name_sex = benef.get("child_name_sex")
    
    #parse mother_name_mother_id
    mother_name = None
    mother_mcts_id = None
    if mother_name_mother_id:
        mother_name_mother_id = mother_name_mother_id.replace("\n","").lower()

        _regSearch = re.search('(\d+)', mother_name_mother_id)
        if _regSearch:
            mother_mcts_id = _regSearch.group(0)

        _regSearch = re.search('([a-z/ ]+)', mother_name_mother_id)
        if _regSearch:
            mother_name = _regSearch.group(0).strip()

    #parse child_name_sex
    child_name = None
    child_sex = None
    if child_name_sex:
        child_name_sex = child_name_sex.replace("\n","").lower()
        child_details = child_name_sex.split("(")

        _regSearch = re.search('([a-z ]+)', child_details[0])
        if _regSearch:
            child_name = _regSearch.group(0).strip()

        if len(child_details) > 1:
            _regSearch = re.search('([a-z]+)', child_details[1])
            if _regSearch:
                child_sex = _regSearch.group(0).strip()
    
    #parse overdue services
    od_services = []
    if overDue_services:
        overDue_services = overDue_services.replace("\n","").lower()
        od_services = overDue_services.split(",")

    gn_services = []
    if given_services:
        given_services = given_services.replace("\n","").lower()
        gn_services = given_services.split(",")

    d_services = []
    if due_services:
        due_services = due_services.replace("\n", "").lower()
        d_services = due_services.split(",")

    #parse lmp_date
    if birthdate:
        birthdate = datetime.datetime.strptime(birthdate, "%d/%m/%Y").date()
    else:
        birthdate = None

    #parse village
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
    
    #parse phone
    phone = None
    phone_type = None
    if phone_no_of_whom:
        raw_phone = phone_no_of_whom.replace("\n","").lower()

        _regSearch = re.search('(\d+)', raw_phone)
        if _regSearch:
            phone = _regSearch.group(0)

        _regSearch = re.search('([a-z]+)', raw_phone)
        if _regSearch:
            phone_type_str = _regSearch.group(0).lower()
            phone_type = Beneficiary.NUMBER_TYPE_MAP.get(phone_type_str)
            if phone_type is None:
                phone_type = 0

    #parse mother mcts id
    child_mcts_id = None
    if year_of_reg_child_id:
        child_mcts_id = year_of_reg_child_id.replace(" ","").replace("\n","").replace("(","").replace(")","_").replace("-","_")

    #parse ASHA phone, name
    asha_name = None
    asha_phone = ''
    if asha_phone_name:
        asha_phone_name = asha_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', asha_phone_name)
        if _regSearch:
            asha_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', asha_phone_name)
        if _regSearch:
            asha_name = _regSearch.group(0).strip()

    #parse anm phone, name
    anm_name = None
    anm_phone = ''
    if anm_phone_name:
        anm_phone_name = anm_phone_name.replace("\n","").lower()

        _regSearch = re.search('(\d+)', anm_phone_name)
        if _regSearch:
            anm_phone = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', anm_phone_name)
        if _regSearch:
            anm_name = _regSearch.group(0).strip()

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

    #check and create care giver
    if asha_name:
        cgs = CareGiver.objects.filter(first_name=asha_name, designation='ASHA', phone=asha_phone)
        if cgs.count() > 0:
            cg = cgs[0]
        else:
            username = asha_name+"_"+asha_phone+"_ASHA"
            username = username[0:29]
            cg = CareGiver.objects.create(first_name=asha_name, designation='ASHA', phone=asha_phone, address=village, username=username)
    else:
        cg = None

    #check and create care provider
    if anm_name:
        cps = CareProvider.objects.filter(first_name=anm_name, designation='ANM', phone=anm_phone)
        if cps.count() > 0:
            cp = cps[0]
        else:
            username = anm_name +"_"+anm_phone+"_ANM"
            username = username[0:29]
            cp = CareProvider.objects.create(first_name=anm_name, designation='ANM', phone=anm_phone, username=username)
    else:
        cp = None

    #check and create IMM benefeciary
    imm_benefs = IMMBenef.objects.filter(MCTS_ID = child_mcts_id)
    if imm_benefs.count() > 0:
        imm_benef = imm_benefs[0]
        print 'Beneficiary Exists'
    else:
        username = child_mcts_id+"_"+child_name
        username = username[0:29]
        imm_benef = IMMBenef.objects.create(dob = birthdate, child_name=child_name, child_sex=child_sex, \
        mother_name=mother_name, mother_mcts_id= mother_mcts_id, active=True, MCTS_ID=child_mcts_id, \
        notify_number=phone, notify_number_type= phone_type, address=village, \
        createdon=utcnow_aware(), modifiedon=utcnow_aware(), subcenter=subcenter, \
        first_name=child_name, caregiver=cg, careprovider=cp, username=username)
        #create beneficiary registration transaction
        events = Events.objects.filter(val=Events.IMM_REG_VAL)
        if events.count() > 0:
            event = events[0]
        else:
            event = Events.objects.create(val=Events.IMM_REG_VAL)
        
        try:
            Transactions.objects.create(event=event, subcenter=subcenter, beneficiary= imm_benef, timestamp=date_then)
        except:
            print "Tried to create imm_reg Transactions without benefeciary"


    #check and create events
    for service in d_services + od_services + gn_services:
        service = service.strip()
        scs = Events.objects.filter(val=service)
        if scs.count() == 0:
            event = Events.objects.create(val=service)

    #create DueEvents
    for service in d_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        des = DueEvents.objects.all().filter(event=event, subcenter=subcenter, beneficiary=imm_benef, date__month=date_then.month, date__year=date_then.year)
        if des:
            print 'Due service already exists'
            continue
        try:
            DueEvents.objects.create(event=event, subcenter=subcenter, beneficiary= imm_benef, date=date_then)
        except:
            print "Tried to create DueEvents without benefeciary"
    #create over due events
    for service in od_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        odes = OverDueEvents.objects.all().filter(event=event, subcenter=subcenter, beneficiary=imm_benef, date__month=date_then.month, date__year=date_then.year)
        if odes:
            print 'OverDue service already exists'
            continue
        try:
            OverDueEvents.objects.create(event=event, subcenter=subcenter, beneficiary= imm_benef, date=date_then)
        except:
            print "Tried to create OverDueEvents without benefeciary"
    #check and create Transactions
    for service in gn_services:
        service = service.strip()
        event = Events.objects.get(val=service)
        dt_then = datetime.datetime.combine(date_then, datetime.datetime.min.time())  + datetime.timedelta(days=1)
        dt_cutoff = utcnow_aware() - datetime.timedelta(days=IMMBenef.IMM_SPAN)
        txs = Transactions.objects.filter(beneficiary=imm_benef, event=event, timestamp__gt = dt_cutoff)
        if txs.count() > 0:
            print 'Transaction service already exists'
            continue
        try:
            Transactions.objects.create(event=event, subcenter=subcenter, beneficiary= imm_benef, timestamp=date_then)
        except:
            print "Tried to create Transactions without benefeciary"

def GetFacilityFromString(fac_str):
    mcts_id = None
    name = None
    if fac_str:
        fac_str = fac_str.replace("\n","").lower()

        _regSearch = re.search('(\d+)', fac_str)
        if _regSearch:
            mcts_id = _regSearch.group(0)

        _regSearch = re.search('([a-z ]+)', fac_str)
        if _regSearch:
            name = _regSearch.group(0).strip()
        if not name and not mcts_id:
            return None
        return (name, mcts_id)    
    else:
        return None

def UploadAndSave(request):
    # Handle file upload
    if request.method == 'POST':        
        input_excel = request.FILES['file']
        benef_type = request.POST.get('benef_type')

        book = xlrd.open_workbook(file_contents=input_excel.read())
        sheet = book.sheet_by_index(0)
        initialIndex = 0
        workplan_list = []

        w=0
        while(1==1):
            w=w+1
            startIndex = getStartingRow(sheet, initialIndex)
           
            if startIndex == "NoData":
                break
            else:
                chunk_dict={}
                columnArray = []
                dict_header = getHeaderDict(sheet, initialIndex, startIndex)
                columnArray = getColumnNames(sheet, startIndex)
                #print "colIndexes="+str(colIndexes)
                rowIndex= startIndex                
                t=0
                row_list=[]
                dict_row = {}
                rowIndex=rowIndex+1
                try:
                    while sheet.cell_value(rowIndex,colIndexes[0])!="" and sheet.cell_value(rowIndex,colIndexes[1])!="":
                       
                        t=t+1
                        dict_row = getRowDict(rowIndex, columnArray , sheet)
                       
                        row_list.append(dict_row)
                        rowIndex=rowIndex+1
                except:
                    print "Exception Main Loop"

                chunk_dict["header"] = dict_header
                chunk_dict["data"] = row_list
                workplan_list.append(chunk_dict)
                initialIndex = rowIndex
        
        _fileObject = None
        for workplan_chunk in workplan_list:           
            header = workplan_chunk["header"]
            data = workplan_chunk["data"]

            if len(data) == 0:
                continue

            #header data
            block = header.get("Health_Block").replace("\n","").strip()
            district = header.get("District").replace("\n","").strip()
            health_facility = header.get("Health_Facility").replace("\n","").strip()
            month = header.get("ReportMonth").replace("\n","").strip()
            year = header.get("ReportYear").replace("\n","").strip()
            state = header.get("State").replace("\n","").strip()
            subfacility = header.get("SubFacility").replace("\n","").strip()
            subfacility_id = header.get("SubFacilityID").replace("\n","").strip()
            
            stamp = benef_type+"_"+state+"_"+district+"_"+block+"_"+health_facility+"_"+subfacility+"_"+subfacility_id+"_"+year+"_"+state
            if not AvailableMCTSData.objects.filter(stamp=stamp):
                chunk = AvailableMCTSData.objects.create(stamp= stamp, benef_type=benef_type, block=block, district=district, health_facility=health_facility, month=month, year=year, state=state, subfacility=subfacility, subfacility_id=subfacility_id, time_stamp=utcnow_aware())
       
            timezone = 'Asia/Kolkata'
            tz = pytz.timezone(timezone)
            today_utc = utcnow_aware()
            today = today_utc.astimezone(tz)
            #create then date, which is 1st of given month 12:00 PM noon IST
            if month and year:
                date_str = month+','+year
                date_then = datetime.datetime.strptime(date_str, "%B,%Y")
                date_then = date_then + datetime.timedelta(hours=12)
                date_then = date_then.replace(second=0)
            else:
                date_then = today.replace(hour=12, minute=0, day=1, second=0).astimezone(pytz.utc)

            t_district = GetFacilityFromString(district)
            t_block = GetFacilityFromString(block)
            t_health_facility = GetFacilityFromString(health_facility)

            #check and create district
            if t_district:
                dsts = District.objects.filter(MCTS_ID = t_district[1])
                if dsts.count()>0:
                    district = dsts[0]
                else:
                    district = District.objects.create(MCTS_ID = t_district[1], name=t_district[0])
            else:
                district = None

            #check and create block
            if t_block:
                blocks = Block.objects.filter(MCTS_ID = t_block[1])
                if blocks.count()>0:
                    block = blocks[0]
                else:
                    block = Block.objects.create(MCTS_ID = t_block[1], name=t_block[0])
            else:
                block = None

            #check and create health facility
            if t_health_facility:
                hfs = HealthFacility.objects.filter(MCTS_ID = t_health_facility[1])
                if hfs.count()>0:
                    health_facility = hfs[0]
                else:
                    health_facility = HealthFacility.objects.create(MCTS_ID = t_health_facility[1], name = t_health_facility[0])
            else:
                health_facility = None

            #check and create subcenter
            sbs = SubCenter.objects.filter(MCTS_ID = subfacility_id)
            if sbs.count() > 0:
                subfacility = sbs[0]
            else:
                subfacility = SubCenter.objects.create(MCTS_ID = subfacility_id, name=subfacility, district=district, block=block, health_facility=health_facility)

            for benef in data:
                if benef_type == 'ANC':
                    print 'Prcessing subcenter for ANC'
                    SaveANCBeneficiary(benef=benef, subcenter=subfacility, date_then=date_then)
                elif benef_type == 'PNC':
                    SavePNCBeneficiary(benef=benef, subcenter=subfacility)
                elif benef_type == 'IMM1' or benef_type == 'IMM2':
                    SaveIMMBeneficiary(benef=benef, subcenter=subfacility, date_then=date_then)
                    pass

        #print workplan_list
        print workplan_list[0]["header"]
        print workplan_list[0]["data"][0]
        print workplan_list[0]["data"][len(workplan_list[0]["data"])-1]

        parsed = ""
        for wp in workplan_list:
         parsed = parsed + " " +str(len(wp["data"]))

        print parsed
        #newdoc = Document(myfile = request.FILES['file'])
        #newdoc.save()
            # Redirect to the document list after POST
        return HttpResponse('Saved successfully')
    return HttpResponse('Error in saving')

    


def uploadandsaveLangLatData(request):
    # Handle file upload
    if request.method == 'POST':        
        input_file = request.FILES['file']
        file_type = request.POST.get('file_type')
         
        print "hello data"  
        print file_type
        print input_file

        if file_type == "Json" :
            file_contents=input_file.read()
        else:
            return HttpResponse('Error in saving')
  

        data = json.loads(file_contents.strip())
        
        print data
        print data['langlatdata'][0]['lang']

        for blockNumber in range(0,len(data['langlatdata'])):
            getblock = LatLangData.objects.filter(block = data['langlatdata'][blockNumber]['sublock'])
            if getblock.count() > 0:
                print data['langlatdata'][blockNumber]['sublock'];
            else:
                blockreference = getBlockReferenceFromBlock(data['langlatdata'][blockNumber]['sublock']);
                LatLangData.objects.create(lat= data['langlatdata'][blockNumber]['lat'], lang=data['langlatdata'][blockNumber]['lang'], block=data['langlatdata'][blockNumber]['sublock'], blockRefernece=blockreference)
                
        return HttpResponse('Saved successfully')
    return HttpResponse('Error in saving')

def getBlockReferenceFromBlock(block_str):
        sbs = SubCenter.objects.filter(name = block_str)
        if sbs.count() > 0:
            subfacility = block_str
            return subfacility
        else:
        #   We did not find anything metching put some smart logic to get this now    
            return None
    