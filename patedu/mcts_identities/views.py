# Create your views here.
from django.shortcuts import render_to_response, render
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
import json
###############################
from mcts_identities.models import CareProvider

def login_page(request):
    return render(request, "login.html", {})

def login_user(request):
    if request.user.is_authenticated():
        return HttpResponse(json.dumps({'redirect': '/dashboard/'}), content_type="application/json")
    
    if 'username' not in request.POST:
        return HttpResponseBadRequest(json.dumps({'error': 'username is required'}), content_type="application/json")
    if 'password' not in request.POST:
        return HttpResponseBadRequest(json.dumps({'error': 'password is required'}), content_type="application/json")
    
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    # Allow only doctor or staff to login
    if not user:
        return HttpResponseBadRequest(json.dumps({'error': 'Wrong username or password'}), content_type="application/json")
    
    isDoctor = True if CareProvider.objects.filter(username=username, designation = 'DOC').count() > 0 else False
    if not isDoctor:
        return HttpResponseBadRequest(json.dumps({'error': 'User not allowed. Only doctors are allowed to login'}), content_type="application/json")
    
    login(request, user)
    return HttpResponse(json.dumps({'redirect': '/dashboard/'}), content_type="application/json")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login')