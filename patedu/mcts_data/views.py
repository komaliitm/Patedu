import json

from django.http import HttpResponse
from django.template import Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from .forms import Document

from .models import Document

# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django import forms
import xlrd

        

    
list_header =     ['State' , 'District' , 'District_ID' , 'Health Block','Health_Block_ID' ,'Health Facility' ,'Health_Facility_ID', 'SubFacility / SubCentre','Village','ANM :' , 'ReportMonth', 'ReportYear']
list_header_key = ['State' , 'District' , 'District_ID' , 'Health_Block','Health_Block_ID', 'Health_Facility' ,'Health_Facility_ID', 'SubFacility','SubFacilityID ','Village','ANM :' , 'ReportMonth', 'ReportYear']
                                                                                                                                                                              
list_columns_value = ['(Year of registration)\nMother ID' , 'Address(GP Village)' ,'Phone No. of(Phone No.)','Phone No. of(Phone No.)' ,'Phone No. of(Phone No. )' , 'Phone No. of (Phone No. )', 'LMP Date','Overdue Services','OverDue Services', 'Due Services' , 'Mother Name(w/o Husband Name)', 'Given Services' , 'Expected Delivery Date', 'Delivery Type', 'Delivery Date', 'Place Of Delivery' , 'Child Name (Sex )' , 'Mother Name( Mother ID )' , '(Year of registration)\nChild ID', 'Birthdate']
list_columns_key =   ['year_of_reg_mother_id' , 'address' ,'phone_no_of_whom','phone_no_of_whom', 'phone_no_of_whom' ,'phone_no_of_whom' ,'lmp_date','overDue_services','overDue_services', 'due_services' ,'mother_name_husband_name', 'given_services' ,'expected_delivery_date', 'delivery_type' , 'delivery_date' , 'place_of_delivery' , 'child_name_sex' , 'mother_name_mother_id' , '(year_of_reg_child_id' , 'birthdate']



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
            except :
                print "Exception"
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


def UploadAndSave(request):
    # Handle file upload
    if request.method == 'POST':        
        input_excel = request.FILES['file']
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
                


        print workplan_list

        #newdoc = Document(myfile = request.FILES['file'])
        #newdoc.save()
            # Redirect to the document list after POST
        return HttpResponse('Saved successfully')
    return HttpResponse('Error in saving')

    