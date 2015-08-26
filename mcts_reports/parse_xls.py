import os
from xlrd import cellname, open_workbook
import json
import threading

def common(x,path):
    com=[]
    for col in range(x.ncols):
        val=str(x.row(2)[col].value)
        if 'District' in val:
            com.append(val)
        elif 'Block' in val:
            com.append(val)
        elif 'Facility' in val:
            com.append(val)
        elif 'SubCentre' in val:
            com.append(val)
    return com

mother_list=[]
child_list=[]
all_paths=[]
thread_list=[]

rootdir=['./xls/benef_list/8-2014','./xls/benef_list/8-2015']
for var in range(2):
    for subdir, dirs, files in os.walk(rootdir[var]):
        for reqfile in files:
            path=os.path.join(subdir,reqfile)
            all_paths.append(path)
print "done"
            
mc=0
cc=0
thr=0

def process(path,mc,cc):
    try:
        wb=open_workbook(path)
    except:
        return
    x,=wb.sheets()
    
    for i in range(5, x.nrows):
        d=dict()
        for j in range(x.ncols):
            if x.row(i)[j].value != x.row(4)[j].value:
                d[x.row(4)[j].value]=x.row(i)[j].value

        for item in common(x,path):
            d[item]=''

        if 'Mother' in path:
            mother_list.append(d)
            mc+=1
        else:
            child_list.append(d)
            cc+=1
    print 'Mothers: ',mc,' Children: ', cc

for item in all_paths:
    t=threading.Thread(target=process, args=(item,mc,cc,))
    thread_list.append(t)
    thr+=1
    t.start()
    #t.join()
    print "\nThread ",thr," added. \n"
    
print "done", len(all_paths)

for thread in thread_list:
    thread.join()

print len(mother_list)
print len(child_list)

with open('mother2.txt','w') as outfile:
    json.dump(mother_list,outfile)

with open('child2.txt','w') as outfile:
    json.dump(child_list,outfile)
