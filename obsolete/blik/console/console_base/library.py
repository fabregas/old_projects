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

#nodes admin states
NEW_NODE        = 0
ACTIVE_NODE     = 1
INACTIVE_NODE   = 2

#operation statuses map (id: name)
OPER_STATUS_MAP = {0: 'In progress', 1: 'Complete', 2: 'Error'}

def inform_message(message, redirect_link='/', yes_no=None):
    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link, 'yes_no':yes_no})

