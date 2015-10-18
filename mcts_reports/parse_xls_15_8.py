import os
from xlrd import cellname, open_workbook
import json


def common(x,path):
    com=[]
    for col in range(x.ncols):
        val=str(x.row(2)[col].value)
        if 'Distric' in val:
            com.append(val)
        elif 'Bloc' in val:
            com.append(val)
        elif 'Facilit' in val:
            com.append(val)
        elif 'SubCentr' in val:
            com.append(val)
        elif 'Villag' in val:
            com.append(val)
    return com

mother_list=[]
child_list=[]

if len(sys.argv) < 3:
    rootdir=['/home/rohan/2014','/home/rohan/9-2015']
else:
    rootdir = [sys.argv[1], sys.argv[2]]

mc=0
cc=0

for var in range(1,2):
    for subdir, dirs, files in os.walk(rootdir[var]):
        for reqfile in files:
            path=os.path.join(subdir,reqfile)
            try:
                wb=open_workbook(path)
                x,=wb.sheets()
            except:
                continue;
            
            for i in range(5, x.nrows):
                d=dict()
                for item in x.row(2):
                    if item.value!='':
                        try:
                            key,val=item.value.split(':')
                            d[key[:-2]]=val[:-2]
                        except:
                            c= item.value
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

print len(mother_list)
print len(child_list)

with open('mother2.txt','w') as outfile:
    json.dump(mother_list,outfile)

with open('child2.txt','w') as outfile:
    json.dump(child_list,outfile)
