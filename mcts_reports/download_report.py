##################################### Method 1
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text

mcts_jhs_username = "nrhm-mcts-jhansi"
mcts_jhs_passwd = "nrhm-mcts-jhansi"

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

# The site we will navigate into, handling it's session
br.open('http://nrhm-mcts.nic.in/CM/SSO.aspx')

# View available forms
# for f in br.forms():
#     print f

# Select the second (index one) form (the first form is a search query box)
br.select_form(nr=0)

# User credentials
control = br.form.find_control("ddl_state")
print control.name
for item in control.items:
	print " name=%s values=%s" % (item.name, str([label.text  for label in item.get_labels()]))
	control.value = [item.name]
	print br.form['ddl_state']

br.form['ddl_state'] = ["09"]
br.form['TxtUsername'] = mcts_jhs_username
br.form['TxtPwd'] = mcts_jhs_passwd

# Login
#login_response = br.submit()
#print login_response.code

#####################################
# #Open the download report page
# br.open('http://nrhm-mcts.nic.in/CM/SSO.aspx')
# br.select_form(nr=0)