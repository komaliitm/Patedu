import urllib
import requests

'''Scope for Google Calendar'''
gCalScope = 'https://www.googleapis.com/auth/calendar'
'''Readonly scope for Google Calendar'''
gCalReadOnlyScope = 'https://www.googleapis.com/auth/calendar.readonly'
'''Scope for Directory User'''
gUserScope = 'https://www.googleapis.com/auth/admin.directory.user'
'''Scope for Readonly Directory User'''
gUserReadOnlyScope = 'https://www.googleapis.com/auth/admin.directory.user.readonly'


vishal_PromdClientId = '987549226815.apps.googleusercontent.com'
vishal_PromdClientSecret = 'r-E_IK0SylNW4hl25IeKI4Fn' #'wxSihTQjpypKx_cTqpzU34bH'
cRedirectURI = 'urn:ietf:wg:oauth:2.0:oob'
##Got auth code from: https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&client_id=265180596478.apps.googleusercontent.com
##AuthCode for vishal.iiita@gmail.com for calendar is 4/vez9uUZeK0pWV6n-LIKTqh1sKHV6.wr-ViUPj4UUfgrKXntQAax06OJzffgI
#cAuthCode = "4/QrIw1txsoMhWHvumUYZykd97U6N6.gq2NYec4O4kRgrKXntQAax04kSjgfgI"
cAuthCode = '4/V0OISimHHrCoCvrUxZxkD_imWZSd.ojCe_Jcw46sSXE-sT2ZLcbRvu6CxfwI'
cRefreshToken = '1/n5_xz8N5ivd9y2kyPNXJZT5RXvnsbTyudeJRRIcfnMY'

cScope = gCalScope + ' ' + gUserScope
cClientID = vishal_PromdClientId
cClientSecret = vishal_PromdClientSecret

def AuthCodeGeneartor():
    param = {'response_type': 'code',
                    'client_id': cClientID,
                    'redirect_uri': cRedirectURI,
                    'scope': cScope}
    cOauthURL = 'https://accounts.google.com/o/oauth2/auth?' + urllib.urlencode(param)
    print "Go to following URL in Browser and get Auth Code"
    print(cOauthURL)

def RefreshTokenGenerator():
    cTokenURL = 'https://accounts.google.com/o/oauth2/token'
    rsPostData = {'code' : cAuthCode,
                        'client_id' : cClientID,
                        'client_secret' : cClientSecret,
                        'redirect_uri' : cRedirectURI,
                        'grant_type' : 'authorization_code',
                        }

    r = requests.post(cTokenURL, data = rsPostData)
    #print "Access Token ==> " + r.access_token
    #print "Refresh Token ==> " + r.refresh_token
    print r.text['refresh_token']

#AuthCodeGeneartor()
RefreshTokenGenerator()
