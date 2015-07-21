##################################### Method 1
import os
import json
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import datetime
import time
import cookielib
import re
import time
import sys, traceback

LOGIN_URL = 'http://nrhm-mctsrpt.nic.in/MCHRPT/SSO.aspx'
REPORT_URL = 'http://nrhm-mctsrpt.nic.in/MCHRPT/Report/Report_New.aspx'

class GetOutOfLoop( Exception ):
    pass

def authenticate(br):
    br.open(LOGIN_URL)
    br.select_form(nr=0)
    br.form['ddl_state'] = ["09"]
    br.form['TxtUsername'] = mcts_jhs_username
    br.form['TxtPwd'] = mcts_jhs_passwd
    br.form.find_control('stn').readonly = False
    br.form.find_control('stn').value = stn_value
    br.form.find_control('stn').readonly = True
    print br.form.find_control("ddl_state").value
    print br.form.find_control("TxtUsername").value
    print br.form.find_control("TxtPwd").value
    print br.form.find_control('stn').value
    login_response = br.submit()

def browse_report_page(br):
    br.open(REPORT_URL)
    if br.response().geturl() != REPORT_URL or list(br.forms())[0].name != 'form1':
        print "Authenticating again..."
        authenticate(br)
        br.open(REPORT_URL)
        if br.geturl() != REPORT_URL:
            raise Exception("Can't browse report url even after Authenticating.")
    br.select_form(nr=0)

def get_token(br, event_target=None, tsm1=None, client_token_vs=None, client_token_ev=None, report_type=None, \
    year=None, month=None, block=None, phc=None, subcenter=None, village=None, mother=None):
    browse_report_page(br)

    if not client_token_ev or not client_token_vs:
        server_token_vs = br.form["__VIEWSTATE"]
        server_token_ev = br.form["__EVENTVALIDATION"]
        children = []
        return server_token_vs, server_token_ev, children

    for ticker in range(1,3):
        try:
            #Add additional controls for async request
            br.form.new_control('text', 'ToolkitScriptManager1', {'value':''})
            #br.form.new_control('text', 'ToolkitScriptManager1_HiddenField', {'value':''})
            #br.form.new_control('text', '__ASYNCPOST', {'value':'true'})
            br.form.new_control('text', 'Type', {'value':'radioNew'})
            br.form.fixup()

            print "In Token Refresh .... "
            tsmhf_control = br.form.find_control("ToolkitScriptManager1_HiddenField")
            tsm_control = br.form.find_control("ToolkitScriptManager1")
            phc_ctrl = br.form.find_control("CmbPHC")
            subcenter_ctrl = br.form.find_control("CmbSubCentre")
            report_type_ctrl = br.form.find_control("ddlREPORT_TYPE")
            month_ctrl = br.form.find_control("ddl_Month")
            year_ctrl = br.form.find_control("ddlYear")
            block_ctrl = br.form.find_control("CmbBlock")
            village_ctrl = br.form.find_control("CmbVillage")
            view_state_control = br.form.find_control("__VIEWSTATE")
            event_validation_control = br.form.find_control("__EVENTVALIDATION")
            event_target_control = br.form.find_control("__EVENTTARGET")
            mother_ctrl = br.form.find_control("cmb_mtr_cld")

            event_target_control.readonly = False
            event_validation_control.readonly = False
            view_state_control.readonly = False

            event_target_control.value = event_target
            tsm_control.value = tsm1

            report_type_ctrl.value = [report_type]
            tsmhf_control.readonly = False
            tsmhf_control.value = ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en:2a06c7e2-728e-4b15-83d6-9b269fb7261e:475a4ef5:addc6819:5546a2b:d2e10b12:effe2a26:37e2e5c9:5a682656:c7029a2:e9e598a9" 
            tsmhf_control.readonly = True
            
            if year:
                br.form.new_control('text', 'txt_detail_Rpt', {'value':'This report provides the details of Mother and Child registered during a particular year.Parameters required are District > Block > Health Facility > Subcentre.'})
                year_ctrl.value = [year]
                tsmhf_control.readonly = False
                tsmhf_control.value = ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en:2a06c7e2-728e-4b15-83d6-9b269fb7261e:475a4ef5:addc6819:5546a2b:d2e10b12:effe2a26:37e2e5c9:5a682656:c7029a2:e9e598a9;" 
                tsmhf_control.readonly = True
            if month:
                month_ctrl.value=[fin_month]
            if block:
                block_ctrl.value = [block]
            if phc:
                phc_ctrl.value = [phc]
            if subcenter:
                subc_item = mechanize.Item(subcenter_ctrl, {"contents":subcenter, "value":subcenter})
                subc_item.selected = True
            if village:
                village_ctrl.value=[village]
            if mother:
                mother_item = mechanize.Item(mother_ctrl, {"contents":mother, "value":mother})
                mother_item.selected = True

            event_validation_control.value = client_token_ev
            view_state_control.value = client_token_vs
            
            submit_btn_ctrl = br.form.find_control("btnSUBMIT")
            dwld_btn_ctrl = br.form.find_control("btndownload")
            br.form.controls.remove(submit_btn_ctrl)
            br.form.controls.remove(dwld_btn_ctrl)

            #print br.form
            response = br.submit()
            br.select_form(nr=0)
            if village:
               child_ctrl = br.form.find_control("cmb_mtr_cld")
               children = filter(lambda x: x != "0", [item.name for item in child_ctrl.items])      
            elif subcenter:
                child_ctrl = br.form.find_control("CmbVillage")
                children = filter(lambda x: x != "0", [item.name for item in child_ctrl.items])     
            elif phc:
                child_ctrl = br.form.find_control("CmbSubCentre")
                children = filter(lambda x: x != "0", [item.name for item in child_ctrl.items])     
            elif block:
                child_ctrl = br.form.find_control("CmbPHC")
                children = filter(lambda x: x != "0", [item.name for item in child_ctrl.items])
            elif year:
                child_ctrl = br.form.find_control("CmbBlock")
                children = filter(lambda x: x != "0", [item.name for item in child_ctrl.items])
            else:
                children = []
            server_token_vs = br.form["__VIEWSTATE"]
            server_token_ev = br.form["__EVENTVALIDATION"]
            return server_token_vs, server_token_ev, children
        except Exception, e:
            if ticker == 1:
                print "First Error in Token Refresh: ", e, " Will be authenticating, waiting for 1 seconds and retrying."
                print "Error in Token refresh for ", event_target, report_type, year, block, phc, subcenter
                traceback.print_exc(file=sys.stdout)
                authenticate(br)
                browse_report_page(br)
                time.sleep(1)
            else:
                print "Second Error in token refresh: ", e, " Will be breaking."
                exit()


num_months = 6
mcts_jhs_username = "nrhm-up.jh"
mcts_jhs_passwd = "4e4d1b7432c708f094401f4cc7029ccc678e72d3"
stn_value = "637dd3894df6b16a956ab46ed377e5d85a7b2310"

report_types = {
    'registered_benefs':'Report_Resistration.aspx?rpt=Details',
}

dictrict = 'Jhansi'
state = 'UP'
f = open('dump.html', 'w')

# Browser
br = mechanize.Browser()

#Cookie Jar
cj = cookielib.LWPCookieJar()
lng_cookie = cookielib.Cookie(version=0, name='lng', value='en', expires=None, port=None, port_specified=False, domain='nrhm-mctsrpt.nic.in', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, discard=False, comment=None, comment_url=None, rest={'HttpOnly': False}, rfc2109=False)
cj.set_cookie(lng_cookie)

#Browser Options
br.set_cookiejar(cj)
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

#Adding request headers
br.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'),
                    ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
                    ('Accept-Encoding','gzip, deflate'),
                    ('Accept-Language','en-US,en;q=0.8'),
                    ('Cache-Control','max-age=0'),
                    ('Origin','http://nrhm-mctsrpt.nic.in'),
                    ('Proxy-Authorization','Basic dXNlci11dWlkLTg1YWYzNDBhZmYzYjlhMTQxNjNkNWYxOTUzMzRlYjA3OjUzODE2NGUxOGMzNg=='),
                    ('Proxy-Connection','keep-alive')]


# The site we will navigate into, handling it's session
authenticate(br)

init__VS, init__EV, children = get_token(br=br)

dt = datetime.datetime.now().date()
cMonth = dt.month
cYear = dt.year
cFinYear = cYear-1 if cMonth <= 3 else cYear
latestMonthInFinYear = str(cMonth)+'/'+str(cYear)

year_iterator = {
    str(cFinYear):str(cMonth)+'/'+str(cYear),
    str(cFinYear-1):'3/'+str(cFinYear)
}

num_reports = 0
try:
    for benef_type, report_type in report_types.iteritems():  
        __VS1, __EV1, children1 = get_token(br=br, event_target="ddlREPORT_TYPE", tsm1="ToolkitScriptManager1|ddlREPORT_TYPE", \
            client_token_vs=init__VS, client_token_ev=init__EV, report_type=report_type)
        for fin_year, fin_month in year_iterator.iteritems():
            __VS2, __EV2, block_list = get_token(br=br, event_target="ddlYear", tsm1="UP1|ddlYear", \
                client_token_vs=__VS1, client_token_ev=__EV1, report_type=report_type, year=fin_year, mother="Mother_Details")
            for block in block_list:
                __VS3, __EV3, phc_list = get_token(br=br, event_target="CmbBlock", tsm1="UP12|CmbBlock", \
                    client_token_vs=__VS2, client_token_ev=__EV2, report_type=report_type, year=fin_year, month=fin_month, mother="Mother_Details", block=block)
                for phc in phc_list:
                    __VS4, __EV4, subc_list = get_token(br=br, event_target="CmbPHC", tsm1="UP13|CmbPHC", \
                        client_token_vs=__VS3, client_token_ev=__EV3, report_type=report_type, year=fin_year, month=fin_month, mother="Mother_Details",block=block,phc=phc)                    
                    for subc in subc_list:
                        __VS5, __EV5, village_list = get_token(br=br, event_target="CmbSubCentre", tsm1="UP14|CmbSubCentre", \
                            client_token_vs=__VS4, client_token_ev=__EV4, report_type=report_type, year=fin_year, month=fin_month, mother="Mother_Details",block=block,phc=phc,subcenter=subc)
                        for ticker in range(1,3):
                            try:
                                file_name = "DetailsMother_"+dictrict+"_"+state+"_"+str(block)+"_"+str(subc)+".xls"
                                file_path = "xls/"+str(cMonth)+"-"+str(cYear)+"/"+state+"/"+dictrict+"/"+str(block)+"/"+str(subc)
                                file_abs_path = os.path.join(file_path, file_name)

                                if os.path.isfile(file_abs_path):
                                    print "File "+file_abs_path+" already exists. Skipping..."
                                    continue

                                browse_report_page(br)
                                print "\n\n\n Opening page..." + str(br.response().code)
                                #Adding missing controls
                                br.form.new_control('text', 'txt_detail_Rpt', {'value':'This report provides the details of Mother and Child registered during a particular year.Parameters required are District > Block > Health Facility > Subcentre.'})
                                br.form.new_control('text', 'Type', {'value':'radioNew'})

                                #facility_ctrl=br.form.find_control("CmbFacilityType")
                                tsmhf_control = br.form.find_control("ToolkitScriptManager1_HiddenField")
                                phc_ctrl = br.form.find_control("CmbPHC")
                                subcenter_ctrl = br.form.find_control("CmbSubCentre")
                                report_type_ctrl = br.form.find_control("ddlREPORT_TYPE")
                                month_ctrl = br.form.find_control("ddl_Month")
                                year_ctrl = br.form.find_control("ddlYear")
                                block_ctrl = br.form.find_control("CmbBlock")
                                submit_btn_ctrl = br.form.find_control("btnSUBMIT")
                                dwld_btn_ctrl = br.form.find_control("btndownload")
                                village_ctrl=br.form.find_control("CmbVillage")
                                mother_ctrl=br.form.find_control("cmb_mtr_cld")
                                #category_ctrl=br.form.find_control("CmbCategory")
                                view_state_control = br.form.find_control("__VIEWSTATE")
                                event_validation_control = br.form.find_control("__EVENTVALIDATION")
                                
                                #Remove extra controls
                                br.form.controls.remove(submit_btn_ctrl)
                                # br.form.controls.remove(br.form.find_control("CmbBeneficiary"))
                                br.form.controls.remove(br.form.find_control("CmbDistrict"))
                                br.form.controls.remove(br.form.find_control("TxtStateCode"))
                                # br.form.controls.remove(br.form.find_control("State_Code"))

                                month_ctrl.value = [fin_month]
                                year_ctrl.value = [fin_year]
                                block_ctrl.value = [str(block)]
                                phc_ctrl.value = [str(phc)]
                                subc_item = mechanize.Item(subcenter_ctrl, {"contents":str(subc), "value":str(subc)})
                                subc_item.selected = True

                                view_state_control.readonly = False
                                event_validation_control.readonly = False
                                event_validation_control.value = __EV5
                                view_state_control.value = __VS5
                                view_state_control.readonly = True
                                event_validation_control.readonly = True    

                                tsmhf_control.readonly = False
                                tsmhf_control.value = ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en:2a06c7e2-728e-4b15-83d6-9b269fb7261e:475a4ef5:addc6819:5546a2b:d2e10b12:effe2a26:37e2e5c9:5a682656:c7029a2:e9e598a9;" 
                                tsmhf_control.readonly = True

                                report_type_ctrl.value = [report_type]

                                print "Downloading below report...."
                                #print month_ctrl.value
                                print block_ctrl.value
                                print phc_ctrl.value
                                print subcenter_ctrl.value
                                print report_type_ctrl.value                    
                                
                                #Submit the form
                                response = br.submit()
                                print "Submitted report download form..." + str(br.response().code)

                                #Find the report URL
                                regex = "(gid=.{64})"
                                m = re.search(regex, response.read())
                                gid_param = m.group(0)

                                #Generate report
                                report_uri = "http://nrhm-mctsrpt.nic.in/MCHRPT/Report/Report_Resistration.aspx?rpt=DetailsMother&"+gid_param
                                file_name = "DetailsMother_"+dictrict+"_"+state+"_"+str(block)+"_"+str(subc)+".xls"
                                file_path = "xls/"+str(cMonth)+"-"+str(cYear)+"/"+state+"/"+dictrict+"/"+str(block)+"/"+str(subc)
                                try:
                                    os.makedirs(file_path)
                                except:
                                    pass
                                
                                print report_uri
                                br.retrieve(report_uri, file_abs_path)
                                num_reports = num_reports + 1
                                break
                            except Exception, e:
                                if ticker == 1:
                                    print "\n\n\n Error while downloading below report...."
                                    print month_ctrl.value
                                    print block_ctrl.value
                                    print phc_ctrl.value
                                    print subcenter_ctrl.value
                                    print report_type_ctrl.value
                                    print "First Error in fetch file: ", e, " Will be authenticating, waiting for 2 seconds and retrying."
                                    authenticate(br)
                                    time.sleep(1)
                                else:
                                    print "Second Error: ", e, " Will be breaking."
                                    print "\n\n\n Error while downloading below report...."
                                    print month_ctrl.value
                                    print block_ctrl.value
                                    print phc_ctrl.value
                                    print subcenter_ctrl.value
                                    print report_type_ctrl.value
                                    print "Error message as: %s" % e
                                    f.write(br.response().read())
                                    exit()
            if cMonth == 0:
                cYear = cYear - 1
                cMonth = 12
            cFinYear = cYear-1 if cMonth <= 3 else cYear
except GetOutOfLoop:
    pass

f.close()
