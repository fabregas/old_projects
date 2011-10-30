from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect

def inform_message(message, redirect_link='/', yes_no=None):
    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link, 'yes_no':yes_no})


