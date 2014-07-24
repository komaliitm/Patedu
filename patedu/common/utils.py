import base64
import uuid
#from django.contrib.auth.models import User
from django.conf import settings
from datetime import date, datetime, time
from functools import reduce
import sys
import os
import time
import inspect
import colorama
from django.utils.timezone import utc


def utcnow_aware():
    return datetime.now().replace(tzinfo=utc)

def pprint(*arg):    
    if not settings.PPRINT_ENABLE:
        return
    msg = reduce(lambda x,y: str(x)+" "+str(y), arg)
    curframe = inspect.currentframe()
    outerframes = inspect.getouterframes(curframe, 2)
    colorama.init()
    print ("["+getPrintablePathForFile(outerframes[1][1])+" ~"+str(outerframes[1][2])+ "]"),    
    print (colorama.Fore.CYAN + colorama.Style.BRIGHT + str(msg)),
    print(colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL)

def get_a_Uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')