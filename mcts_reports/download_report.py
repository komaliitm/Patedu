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

LOGIN_URL = 'http://nrhm-mctsrpt.nic.in/MCHRPT/SSO.aspx'
WORKPLAN_URL = 'http://nrhm-mctsrpt.nic.in/MCHRPT/Workplan/Rpt_WorkPlan.aspx'

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

def browse_workplan_page(br):
	br.open(WORKPLAN_URL)
	if br.geturl() != WORKPLAN_URL:
		print "Authenticating again..."
		authenticate(br)
		br.open(WORKPLAN_URL)
		if br.geturl() != WORKPLAN_URL:
			raise Exception("Can't browse wrokplan  url even after Authenticating.")
	br.select_form(nr=0)

def get_token(br, event_target=None, tsm1=None, client_token_vs=None, client_token_ev=None, report_type=None, \
	year=None, month=None, block=None, phc=None, subcenter=None):
	browse_workplan_page(br)

	if not client_token_ev or not client_token_vs:
		server_token_vs = br.form["__VIEWSTATE"]
		server_token_ev = br.form["__EVENTVALIDATION"]
		children = []
		return server_token_vs, server_token_ev, children

	#Add additional controls for async request
	br.form.new_control('text', 'ToolkitScriptManager1', {'value':''})
	#br.form.new_control('text', '__ASYNCPOST', {'value':'true'})
	br.form.fixup()

	#Add the values to controls
	tsm_control = br.form.find_control("ToolkitScriptManager1")
	phc_ctrl = br.form.find_control("CmbPHC")
	subcenter_ctrl = br.form.find_control("CmbSubCentre")
	report_type_ctrl = br.form.find_control("ddlWorkPlan_TYPE")
	month_ctrl = br.form.find_control("ddl_Month")
	year_ctrl = br.form.find_control("ddlYear")
	block_ctrl = br.form.find_control("CmbBlock")
	view_state_control = br.form.find_control("__VIEWSTATE")
	event_validation_control = br.form.find_control("__EVENTVALIDATION")
	event_target_control = br.form.find_control("__EVENTTARGET")

	event_target_control.readonly = False
	event_validation_control.readonly = False
	view_state_control.readonly = False

	event_target_control.value = event_target
	tsm_control.value = tsm1
	report_type_ctrl.value = [report_type]
	if year and month:
		month_ctrl.value = [month]
		year_ctrl.value = [year]
	if block:
		block_ctrl.value = [block]
	if phc:
		phc_ctrl.value = [phc]
	if subcenter:
		subc_item = mechanize.Item(subcenter_ctrl, {"contents":subcenter, "value":subcenter})
		subc_item.selected = True

	event_validation_control.value = client_token_ev
	view_state_control.value = client_token_vs
	
	submit_btn_ctrl = br.form.find_control("btnSUBMIT")
	dwld_btn_ctrl = br.form.find_control("btndownload")
	br.form.controls.remove(submit_btn_ctrl)
	br.form.controls.remove(dwld_btn_ctrl)

	#print br.form
	response = br.submit()
	br.select_form(nr=0)
	if phc:
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

num_months = 6
mcts_jhs_username = "nrhm-up.jh"
mcts_jhs_passwd = "4e4d1b7432c708f094401f4cc7029ccc678e72d3"
stn_value = "637dd3894df6b16a956ab46ed377e5d85a7b2310"
# district_map = {
# 	400:{
# 		1609:[10115, 10116, 24098, 10120, 10123, 10122, 10124, 10119, 10121, 23956, 10118, 10117, 23954, 10125, 23957 ],
# 		1612:[10148, 10139, 10140, 10142, 10144, 10149, 10145, 10147, 10146, 10141, 10150, 26350, 10143],
# 		1611:[10137, 26352, 10134, 10135, 10138, 26353, 10136],
# 		1613:[10153, 10154, 26351, 10155, 10152, 10151, 10156],
# 		1610:[10132, 10129, 10130, 10127, 10128, 10131, 10133, 10126]
# 	},
# 	401:{
# 		1614:[10157, 10158, 10163, 10159, 10164, 24306, 10161, 10162, 10160, 10165],
# 		1615:[10170, 10173, 10166, 10172, 10168, 10174, 10167, 10171, 10169],
# 		1617:[10184, 25357, 10188, 10186, 10185, 10187, 25359, 25358],
# 		1618:[10190, 10191, 10194, 10189, 25356, 10193, 10192, 10195],
# 		1616:[25355, 10183, 10180, 10181, 10179, 10182, 10178, 10177, 10175, 10176]
# 	},
# 	396:{},
# 	398:{},
# 	395:{},
# 	397:{},
# 	399:{},
# 	394:{}
# }

report_types = {
	'ANC':'Rpt_WorkPlan_Registration.aspx?rpt=wpwa', 
	'INF_IMM':'Rpt_WorkPlan_Registration.aspx?rpt=wii',
	'CHILD_IMM':'Rpt_WorkPlan_Registration.aspx?rpt=wci'
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
num_reports = 0
try:
	for benef_type, report_type in report_types.iteritems():  
		__VS1, __EV1, children1 = get_token(br=br, event_target="ddlWorkPlan_TYPE", tsm1="ToolkitScriptManager1|ddlWorkPlan_TYPE", \
			client_token_vs=init__VS, client_token_ev=init__EV, report_type=report_type)
		for i in range(1,num_months):
			__VS2, __EV2, block_list = get_token(br=br, event_target="ddlYear", tsm1="ToolkitScriptManager1|ddlYear", \
				client_token_vs=__VS1, client_token_ev=__EV1, report_type=report_type, year=str(cFinYear), month=str(cMonth)+"/"+str(cYear))
			for block in block_list:
				__VS3, __EV3, phc_list = get_token(br=br, event_target="CmbBlock", tsm1="UpdatePanel9|CmbBlock", \
					client_token_vs=__VS2, client_token_ev=__EV2, report_type=report_type, year=str(cFinYear), month=str(cMonth)+"/"+str(cYear), block=str(block))
				for phc in phc_list:
					__VS4, __EV4, subc_list = get_token(br=br, event_target="CmbPHC", tsm1="UpdatePanel10|CmbPHC", \
						client_token_vs=__VS3, client_token_ev=__EV3, report_type=report_type, year=str(cFinYear), month=str(cMonth)+"/"+str(cYear), block=str(block), phc=str(phc))					
					for subc in subc_list:
						try:
							file_name = benef_type+"_"+dictrict+"_"+state+"_"+str(block)+"_"+str(subc)+".xls"
							file_path = "xls/"+str(cMonth)+"-"+str(cYear)+"/"+state+"/"+dictrict+"/"+str(block)+"/"+str(subc)
							file_abs_path = os.path.join(file_path, file_name)

							if os.path.isfile(file_abs_path):
								print "File "+file_abs_path+" already exists. Skipping..."
								continue;

							browse_workplan_page(br)
							print "\n\n\n Opening page..." + str(br.response().code)
							
							phc_ctrl = br.form.find_control("CmbPHC")
							subcenter_ctrl = br.form.find_control("CmbSubCentre")
							report_type_ctrl = br.form.find_control("ddlWorkPlan_TYPE")
							month_ctrl = br.form.find_control("ddl_Month")
							year_ctrl = br.form.find_control("ddlYear")
							block_ctrl = br.form.find_control("CmbBlock")
							submit_btn_ctrl = br.form.find_control("btnSUBMIT")
							dwld_btn_ctrl = br.form.find_control("btndownload")
							view_state_control = br.form.find_control("__VIEWSTATE")
							event_validation_control = br.form.find_control("__EVENTVALIDATION")
							
							view_state_control.readonly = False
							event_validation_control.readonly = False

							#Remove extra controls
							br.form.controls.remove(submit_btn_ctrl)
							br.form.controls.remove(br.form.find_control("CmbBeneficiary"))
							br.form.controls.remove(br.form.find_control("CmbDistrict"))
							br.form.controls.remove(br.form.find_control("TxtStateCode"))
							br.form.controls.remove(br.form.find_control("State_Code"))

							month_ctrl.value = [str(cMonth)+"/"+str(cYear)]
							year_ctrl.value = [str(cFinYear)]
							block_ctrl.value = [str(block)]
							phc_ctrl.value = [str(phc)]
							subc_item = mechanize.Item(subcenter_ctrl, {"contents":str(subc), "value":str(subc)})
							subc_item.selected = True

							event_validation_control.value = __EV4
							view_state_control.value = __VS4
							
							report_type_ctrl.value = [report_type]

							print "Downloading below report...."
							print month_ctrl.value
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
							report_uri = "http://nrhm-mctsrpt.nic.in/MCHRPT/Workplan/"+report_type+"&"+gid_param
							file_name = benef_type+"_"+dictrict+"_"+state+"_"+str(block)+"_"+str(subc)+".xls"
							file_path = "xls/"+str(cMonth)+"-"+str(cYear)+"/"+state+"/"+dictrict+"/"+str(block)+"/"+str(subc)
							try:
								os.makedirs(file_path)
							except:
								pass
							
							print report_uri
							br.retrieve(report_uri, file_abs_path)
							num_reports = num_reports + 1
						except Exception,e:
							print "\n\n\n Error while downloading below report...."
							print month_ctrl.value
							print block_ctrl.value
							print phc_ctrl.value
							print subcenter_ctrl.value
							print report_type_ctrl.value
							print br.response().code
							print "Error message as: %s" % e
							f.write(br.response().read())
			if cMonth == 0:
				cYear = cYear - 1
				cMonth = 12
			cFinYear = cYear-1 if cMonth <= 3 else cYear
except GetOutOfLoop:
    pass

f.close()