from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import json

def index(request):
    return render_to_response('base.html')

def get_menu_items(request):
    menu_data = []

    '''
    Menu example:

        [{'id': 'test_item1',
            'label': 'Test item #1',
            'url': 'http://google.com',
            'subitems': []
        },
        {'id': 'test_item2',
            'label': 'Test item #2',
            'url': 'http://google.com',
            'subitems': [{
                'id':'test_subitems1',
                'label': 'Test SUBitem #1',
                'url': 'http://google.com',
                'subitems': []
            }],
        }]
    '''

    return HttpResponse(json.dumps(menu_data), mimetype="application/json")

