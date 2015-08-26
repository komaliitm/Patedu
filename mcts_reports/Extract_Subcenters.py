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
	if br.response().geturl() != WORKPLAN_URL or list(br.forms())[0].name != 'form1':
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

	for ticker in range(1,3):
		try:
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
			children = {}
			response = br.submit()
			br.select_form(nr=0)
			if phc:
				child_ctrl = br.form.find_control("CmbSubCentre")
				for item in child_ctrl.items:
					if item.name != "0":
						children[item.name] = str([label.text  for label in item.get_labels()])
			elif block:
				child_ctrl = br.form.find_control("CmbPHC")
				for item in child_ctrl.items:
					if item.name != "0":
						children[item.name] = str([label.text  for label in item.get_labels()])
			elif year:
				child_ctrl = br.form.find_control("CmbBlock")
				for item in child_ctrl.items:
					if item.name != "0":
						children[item.name] = str([label.text  for label in item.get_labels()])

			server_token_vs = br.form["__VIEWSTATE"]
			server_token_ev = br.form["__EVENTVALIDATION"]
			return server_token_vs, server_token_ev, children
		except Exception, e:
			if ticker == 1:
				print "First Error in Token Refresh: ", e, " Will be authenticating, waiting for 1 seconds and retrying."
				print "Error in Token refresh for ", event_target, report_type, year, month, block, phc, subcenter
				authenticate(br)
				browse_workplan_page(br)
				time.sleep(1)
			else:
				print "Second Error in token refresh: ", e, " Will be breaking."
				exit()


num_months = 6
mcts_jhs_username = "nrhm-up.jh"
mcts_jhs_passwd = "4e4d1b7432c708f094401f4cc7029ccc678e72d3"
stn_value = "637dd3894df6b16a956ab46ed377e5d85a7b2310"

report_types = {
	'ANC':'Rpt_WorkPlan_Registration.aspx?rpt=wpwa'
}

dictrict = 'Jhansi'
state = 'UP'
f = open('subc_list.html', 'w')

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
			for block, block_name in block_list.iteritems():
				__VS3, __EV3, phc_list = get_token(br=br, event_target="CmbBlock", tsm1="UpdatePanel9|CmbBlock", \
					client_token_vs=__VS2, client_token_ev=__EV2, report_type=report_type, year=str(cFinYear), month=str(cMonth)+"/"+str(cYear), block=str(block))
				for phc, phc_name in phc_list.iteritems():
					__VS4, __EV4, subc_list = get_token(br=br, event_target="CmbPHC", tsm1="UpdatePanel10|CmbPHC", \
						client_token_vs=__VS3, client_token_ev=__EV3, report_type=report_type, year=str(cFinYear), month=str(cMonth)+"/"+str(cYear), block=str(block), phc=str(phc))					
					for subc, subc_name in subc_list.iteritems():
						f.write("subcenter: "+subc_name+", phc: "+phc_name+", block: "+block_name)
						f.write("\n")
			if cMonth == 0:
				cYear = cYear - 1
				cMonth = 12
			cFinYear = cYear-1 if cMonth <= 3 else cYear
except GetOutOfLoop:
    pass

f.close()