from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from console_base.menu import get_menu
from console_base.auth import get_current_user
from copy import copy
import json

def index(request):
    return render_to_response('base.html')

def _select_user_menu(menu, user):
    ret_menu = []
    for item in menu:
        if item['role'] not in user.roles:
            continue

        item = copy(item)
        if item.children:
            children = _select_user_menu(item.children, user)
            item.children = children

        ret_menu.append(item)

    return ret_menu



def get_menu_items(request):
    '''
    Menu example:

        [{'sid': 'test_item1',
            'label': 'Test item #1',
            'url': 'http://google.com',
            'role': none,
            'children': []
        },
        {'sid': 'test_item2',
            'role': 'admin'
            'label': 'Test item #2',
            'url': 'http://google.com',
            'children': [{
                'sid':'test_subitems1',
                'label': 'Test SUBitem #1',
                'url': 'http://google.com',
                'role': none
                'children': []
            }],
        }]
    '''
    menu = get_menu()

    user = get_current_user(request)

    user_menu = _select_user_menu(menu, user)

    return HttpResponse(json.dumps(user_menu), mimetype="application/json")

