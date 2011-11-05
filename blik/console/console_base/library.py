from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect

#object types
OT_CLUSTER  = 1
OT_NODE     = 2

#parameter type
PT_STRING           = 1
PT_INTEGER          = 2
PT_HIDDEN_STRING    = 4

#display bool values
BOOL_VALS = {True: 'on', False: 'off'}

#splitter symbol for predefined values list
LIST_PARAMETER_SPLITTER = '|'

def inform_message(message, redirect_link='/', yes_no=None):
    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link, 'yes_no':yes_no})

