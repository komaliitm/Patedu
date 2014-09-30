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
    print "initialIndex="
    print initialIndex
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
                    
                    blankCount = 0
                    colIndexes.append(y)
                    columnArray.append(sheet.cell_value(x,y) )
                    colCount = colCount+1
                y= y+1
            except :
                print "Exception"
                break
    
    return columnArray

def getRowDict(rowIndex, columnArray, sheet ):
    dict_cell_value = {}
    y=0
    x = rowIndex

    while y < len(columnArray) :
        dict_cell_value[columnArray[y]] = sheet.cell_value(x,colIndexes[y])
        y=y+1
    return dict_cell_value       

    
list_header = ['State' , 'District' , 'District_ID' , 'Health Block','Health_Block_ID' ,'Health Facility' ,'Health_Facility_ID', 'SubFacility / SubCentre','Village','ANM :']
list_header_key = ['State' , 'District' , 'District_ID' , 'Health_Block','Health_Block_ID', 'Health_Facility' ,'Health_Facility_ID', 'SubFacility','SubFacilityID ','Village','ANM :']



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

    
    
    return dict_header




def UploadAndSave(request):
    # Handle file upload
    if request.method == 'POST':

        print request.FILES.values()
        print request.FILES['file']
        
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
                rowIndex= startIndex                
                t=0
                row_list=[]
                dict_row = {}
                rowIndex=rowIndex+1

                try:
                    while sheet.cell_value(rowIndex,0)!="":
                        t=t+1
                        dict_row = getRowDict(rowIndex, columnArray , sheet)
                        row_list.append(dict_row)
                        rowIndex=rowIndex+1
                except:
                    print "Except all"

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

    