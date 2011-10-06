from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect

def inform_message(message, redirect_link='/', yes_no=None):
    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link, 'yes_no':yes_no})

def authorize(perm):
    '''
    decorator for view authorization
    '''
    def wraper(func):
         def dec_func(request, *args, **kvargs):
             if not is_authenticated(request):
                 return HttpResponseRedirect('/auth')

             if not is_authorize(request, perm):
                 return inform_message('You are not permissed for this action!')

             ret =  func(request, *args, **kvargs)

             return ret

         return dec_func
    return wraper

