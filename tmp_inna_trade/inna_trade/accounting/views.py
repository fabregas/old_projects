# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import hashlib, uuid
from datetime import date,datetime, timedelta
import time
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Min, Sum, Avg
from django.db.models import Q

from models import *

def index(request):
    return HttpResponseRedirect('/orders')

def get_static_page(request, page):
    return render_to_response(page, locals())

def move_order_items_to_store(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        if not order_item.location:
            order_item.location = 'store'
            order_item.save()


@csrf_exempt
def update_order(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    order_id = request.POST['order_id']
    start_order_dt = request.POST['start_order_dt']
    end_order_dt = request.POST['end_order_dt']
    seller = request.POST['seller']
    discount_perc = float(request.POST['discount_perc'])
    course = request.POST['course']
    delivery = request.POST['delivery']

    if discount_perc < 0 or discount_perc > 100:
        raise Exception('Invalid discount value!')

    seller = KeysDict.objects.get(pk=int(seller))
    start_order_dt = datetime.strptime(start_order_dt, '%d.%m.%Y')
    if end_order_dt:
        end_order_dt = datetime.strptime(end_order_dt, '%d.%m.%Y')
        if end_order_dt < start_order_dt:
            return HttpResponse(json.dumps({'ret_code': 1, 'ret_message': 'Mistmatch dates!'}), content_type="application/json")
    else:
        end_order_dt = None
    if not course:
        course = None
    if not delivery:
        delivery = 0


    if order_id:
        order = Order.objects.get(pk=int(order_id))
        if end_order_dt:
            move_order_items_to_store(order)
        order.booking_date = start_order_dt 
        order.receive_date = end_order_dt 
        order.seller = seller
        order.course = course
        order.delivery = delivery
        order.discount_percent = discount_perc
    else:
        order = Order(booking_date=start_order_dt, receive_date=end_order_dt,
                 seller=seller, course=course, delivery=delivery, discount_percent=discount_perc)

    order.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'order_id':order.pk}), content_type="application/json")

@csrf_exempt
def remove_order(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')
    order_id = request.POST['order_id']
    order = Order.objects.get(pk=int(order_id))
    items = OrderItem.objects.filter(order=order)
    items.delete()
    order.delete()
    return HttpResponse(json.dumps({'ret_code': 0}), content_type="application/json")

@csrf_exempt
def remove_order_item(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    item_id = request.POST['item_id']
    order_i = OrderItem.objects.get(pk=int(item_id))
    order_i.delete()
    return HttpResponse(json.dumps({'ret_code': 0}), content_type="application/json")


@csrf_exempt
def update_order_item(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    order_id = request.POST.get('order_id', None)
    order_item_id = request.POST['order_item_id']
    brand = request.POST['brand']
    name = request.POST['item_name']
    option = request.POST['item_option']
    cost = request.POST['cost']
    price = request.POST.get('price', 0)
    price = 0 if not price else float(price)
    notes = request.POST['notes']
    count = request.POST.get('count', '')
    if count:
        count = int(count)
        if count < 1 or count > 100:
            raise Exception('Invalid count value "%s"'%count)
    else:
        count = 1

    brand = get_dict_key(brand, 'brands')
    name = get_dict_key(name, 'item_names')
    option = get_dict_key(option, 'item_options')
    if order_item_id:
        order_i = OrderItem.objects.get(pk=int(order_item_id))
        order_i.brand = brand 
        order_i.name = name 
        order_i.option = option 
        order_i.cost = cost
        order_i.price = price
        order_i.notes = notes
        order_i.save()
    else:
        order = Order.objects.get(pk=int(order_id))
        for i in range(count):
            order_i = OrderItem(order=order, brand=brand, name=name, option=option, cost=cost, notes=notes, price=price)
            if order.receive_date:
                order_i.location = 'store'
            order_i.save()

    return HttpResponse(json.dumps({'ret_code': 0}), content_type="application/json")

@csrf_exempt
def update_item_price(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')
    item_id = int(request.POST['item_id'])
    price = float(request.POST['price'])
    order_i = OrderItem.objects.get(pk=int(item_id))
    order_i.price = price
    order_i.save()
    return HttpResponse(json.dumps({'ret_code': 0}), content_type="application/json")

@csrf_exempt
def sell_item(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    item_id = request.POST['item_id']
    sell_date = request.POST['sell_date']
    shop_seller_id = request.POST['seller']
    buyer = request.POST['buyer']
    discount = request.POST['discount']

    buyer = get_dict_key(buyer, 'buyers')
    order_i = OrderItem.objects.get(pk=int(item_id))
    order_i.shop_seller = KeysDict.objects.get(pk=int(shop_seller_id))
    order_i.sale_date = datetime.strptime(sell_date, '%d.%m.%Y')
    order_i.buyer = buyer
    order_i.discount = float(discount)
    order_i.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'order_id':order_i.pk}), content_type="application/json")

@csrf_exempt
def cancel_sell(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    item_id = request.POST['item_id']
    order_i = OrderItem.objects.get(pk=int(item_id))
    order_i.sale_date = None
    order_i.buyer = None
    order_i.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'order_id':order_i.pk}), content_type="application/json")

@csrf_exempt
def add_item_inout(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    name = request.POST['name']
    price = request.POST['price']
    sell_date = request.POST['sell_date']
    location = request.POST['location']

    name = get_dict_key(name, 'sales_names')
    order_i = OrderItem(name=name, price=float(price), location=location, \
        sale_date=datetime.strptime(sell_date, '%d.%m.%Y'))
    order_i.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'order_id':order_i.pk}), content_type="application/json")

@csrf_exempt
def add_item_embedebts(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    desc = request.POST['desc']
    summ = float(request.POST['sum'])
    em_date = request.POST['date']
    em_date = datetime.strptime(em_date, '%d.%m.%Y')
    item_id = request.POST.get('item_id', None)
    is_repaid = request.POST.get('repaid', None)
    is_repaid = True if is_repaid == 'on' else False
    if item_id:
        item = EmbeddingDebts.objects.get(pk=int(item_id))
        item.description = desc
        item.em_date = em_date
        item.sum = summ
        item.is_repaid = is_repaid
    else:
        item = EmbeddingDebts(description=desc, em_date=em_date, sum=summ, is_repaid=is_repaid)
    item.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'item_id':item.pk}), content_type="application/json")

@csrf_exempt
def remove_item_embedebts(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    item_id = request.POST.get('item_id', None)
    item = EmbeddingDebts.objects.get(pk=int(item_id))
    item.delete()
    return HttpResponse(json.dumps({'ret_code': 0}), content_type="application/json")

@csrf_exempt
def change_item_location(request):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    item_id = request.POST['item_id']
    location = request.POST['location']
    if location not in ('store', 'eurasia', 'asiapark'):
        raise Exception('Unknown location "%s"'%location)

    order_i = OrderItem.objects.get(pk=int(item_id))
    order_i.location = location
    order_i.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'order_id':order_i.pk}), content_type="application/json")


@csrf_exempt
def update_seller(request, dict_type):
    if request.method != 'POST':
        raise Exception('POST method expected!')

    seller = request.POST['seller'].strip()
    if not seller:
        raise Exception('Seller is empty!')

    s = KeysDict(dict_type=dict_type, key=seller)
    s.save()
    return HttpResponse(json.dumps({'ret_code': 0, 'seller_id': s.pk}), content_type="application/json")


def get_dict_key(key, dict_type):
    if not key:
        return None
    vals = KeysDict.objects.filter(dict_type=dict_type, key=key)
    if vals:
        return vals[0]

    key_o = KeysDict(dict_type=dict_type, key=key)
    key_o.save()
    return key_o


def get_sellers(request, dict_type):
    all_sellers = KeysDict.objects.filter(dict_type=dict_type)
    sellers = [(s.pk, s.key) for s in all_sellers]

    return HttpResponse(json.dumps(sellers), content_type="application/json")


def get_order_total(order):
    order_items = OrderItem.objects.filter(order=order).order_by('name__key')
    summ = 0

    for order_item in order_items:
        summ += order_item.cost

    if order.delivery:
        delivery = order.delivery
    else:
        delivery = 0
    summ += delivery
    return summ, delivery, order_items

def get_order_items(order):
    summ, delivery, order_items = get_order_total(order)
    items = []
    init_cost_sum = price_sum = 0
    for order_item in order_items:
        init_cost = ((order_item.cost * (1-order.discount_percent/100.) + ((order_item.cost+0.0)/summ)*delivery) * order.course)
        init_cost_sum += init_cost
        price_sum += order_item.price

        init_cost = '%.2f'%init_cost
        option = '' if not order_item.option else order_item.option.key
        sale_date = None if not order_item.sale_date else order_item.sale_date.strftime('%d.%m.%Y')
        items.append([order_item.pk, order_item.brand.key, order_item.name.key, \
                order_item.cost, order_item.price, order_item.notes, init_cost, option, sale_date])

    return summ, init_cost_sum, price_sum, items

def calculate_order_item(order_item):
    order = order_item.order
    summ, delivery, _ = get_order_total(order)
    init_cost = (order_item.cost * (1-order.discount_percent/100.) + ((order_item.cost+0.0)/summ)*delivery) * order.course
    marg = order_item.price - init_cost - order_item.discount

    return '%.2f'%init_cost, '%.2f'%marg

def calculate_margin_sum(orders_items):
    marg_sum = 0
    price_sum = 0
    for item in orders_items:
        init_cost, marg = calculate_order_item(item)
        marg_sum += float(marg)
        price_sum += item.price
    return price_sum, marg_sum

def get_orders(request):
    page_num = int(request.GET.get('page_num', 1))
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    CNT = 15

    if date_from:
        date_from = datetime.strptime(date_from, '%d.%m.%Y')
    if date_to:
        date_to = datetime.strptime(date_to, '%d.%m.%Y')

    orders_objs = Order.objects
    if date_from == date_to == '':
        orders_objs = orders_objs.all()
    elif date_from == date_to:
        orders_objs = orders_objs.filter(booking_date__gte=date_from, \
            booking_date__lte=date_to)
    elif date_from:
        orders_objs = orders_objs.filter(booking_date__gte=date_from)
    elif date_to:
        orders_objs = orders_objs.filter(booking_date__lte=date_to)
    
    all_cnt = orders_objs.count()
    pages_count = all_cnt / CNT
    if all_cnt % CNT:
        pages_count += 1

    orders_objs = orders_objs.order_by('-booking_date')[(page_num-1)*CNT:page_num*CNT]

    orders = []
    for order in orders_objs:
        received_str = '' if not order.receive_date else order.receive_date.strftime('%d.%m.%Y')
        orders.append((order.pk, [order.seller.key, order.booking_date.strftime('%d.%m.%Y'),\
                    received_str, None, order.course, order.delivery, order.discount_percent]))

    return HttpResponse(json.dumps({'ret_code': 0, 'orders': orders, \
            'pages_count': pages_count or 1, 'page_num': page_num}),\
            content_type="application/json")

def get_all_order_items(request):
    order_id = request.GET.get('order_id', None)

    order = Order.objects.get(id=int(order_id))

    summ, init_cost_sum, price_sum, order_items = get_order_items(order)
    received_str = '' if not order.receive_date else order.receive_date.strftime('%d.%m.%Y')
    return HttpResponse(json.dumps({'ret_code': 0, 'order_items': order_items, \
            'init_cost_sum': '%.2f'%init_cost_sum, 'price_sum': price_sum}),\
            content_type="application/json")

def get_orders_items(request):
    page_num = int(request.GET.get('page_num', 1))
    shop_seller = request.GET.get('shop_seller', '')
    location = request.GET.get('location', '')
    summarize = True if request.GET.get('summarize', 'false') == 'true' else False
    sum_margin = True if request.GET.get('sum_margin', 'false') == 'true' else False
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    brand = request.GET.get('brand', '')
    item_name = request.GET.get('item_name', '')
    buyer = request.GET.get('buyer', '')

    CNT = 50

    if date_from:
        date_from = datetime.strptime(date_from, '%d.%m.%Y')
    if date_to:
        date_to = datetime.strptime(date_to, '%d.%m.%Y')

    orders_items = OrderItem.objects.filter(order__isnull=False)
    if date_from:
        orders_items = orders_items.filter(sale_date__gte=date_from)
    if date_to:
        orders_items = orders_items.filter(sale_date__lte=date_to)

    if brand:
        orders_items = orders_items.filter(brand__key__icontains=brand)
    if item_name:
        orders_items = orders_items.filter(name__key__icontains=item_name)
    if buyer:
        orders_items = orders_items.filter(buyer__key=buyer)


    if location in ('', 'all'):
        if summarize:
            orders_items = orders_items.filter(location__isnull=False)
        else:
            orders_items = orders_items.filter(location__isnull=False, sale_date__isnull=True)
    elif location == 'in_transit':
        orders_items = orders_items.filter(location__isnull=True)
    elif location == 'sold':
        orders_items = orders_items.filter(sale_date__isnull=False)
    else:
        if location not in ('store', 'eurasia', 'asiapark'):
            raise Exception('Unknown location "%s"'%location)

        if summarize:
            orders_items = orders_items.filter(location=location)
        else:
            orders_items = orders_items.filter(location=location, sale_date__isnull=True)

    if shop_seller:
        shop_seller = KeysDict.objects.get(pk=int(shop_seller))
        orders_items = orders_items.filter(shop_seller=shop_seller)

    all_cnt = orders_items.count()
    pages_count = all_cnt / CNT
    if all_cnt % CNT:
        pages_count += 1

    price_sum = margin_sum = five_perc = 0
    if summarize:
        price_sum = orders_items.aggregate(Sum('price'))['price__sum']

    if sum_margin:
        price_sum, margin_sum = calculate_margin_sum(orders_items)
        price_sum = '%.2f'% price_sum
        margin_sum = '%.2f'%margin_sum

    if location == 'sold':
        orders_items = orders_items.order_by('-sale_date')
    else:
        orders_items = orders_items.order_by('brand__key', 'name__key', 'order__receive_date')

    orders_items = orders_items[(page_num-1)*CNT:page_num*CNT]

    items = []
    for item_o in orders_items:
        item = {}
        item['brand'] = item_o.brand.key
        item['name'] = item_o.name.key
        if item_o.option:
            item['name'] += ' (%s)'%item_o.option.key
        item['cost'] = item_o.cost
        item['price'] = item_o.price - item_o.discount
        item['notes'] = item_o.notes
        item['buyer'] = '' if not item_o.buyer else item_o.buyer.key
        item['location'] = item_o.location
        item['shop_seller_id'] = None if not item_o.shop_seller else item_o.shop_seller.id
        item['sale_date'] = None if not item_o.sale_date else item_o.sale_date.strftime('%d.%m.%Y')
        item['discount'] = item_o.discount
        item['id'] = item_o.id

        init_cost, marg = calculate_order_item(item_o)
        item['init_cost'] = init_cost
        item['margin'] = marg

        items.append(item)

    if summarize:
        five_perc = '%.2f'%(price_sum * 0.05)
        price_sum = '%.2f'% price_sum

    return HttpResponse(json.dumps({'ret_code': 0, 'items': items, \
            'pages_count': pages_count or 1, 'page_num': page_num, \
            'price_sum': price_sum, 'margin_sum': margin_sum, 'five_perc': five_perc}),\
            content_type="application/json")

def get_incspend_list(request):
    page_num = int(request.GET.get('page_num', 1))
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    CNT = 15

    if date_from:
        date_from = datetime.strptime(date_from, '%d.%m.%Y')
    if date_to:
        date_to = datetime.strptime(date_to, '%d.%m.%Y')

    orders_items = OrderItem.objects.filter(sale_date__isnull=False)
    if date_from:
        orders_items = orders_items.filter(sale_date__gte=date_from)
    if date_to:
        orders_items = orders_items.filter(sale_date__lte=date_to)

    all_cnt = orders_items.count()
    pages_count = all_cnt / CNT
    if all_cnt % CNT:
        pages_count += 1

    orders_items = orders_items.order_by('-sale_date')[(page_num-1)*CNT:page_num*CNT]

    items = []
    for item_o in orders_items:
        item = {}
        item['name'] = item_o.name.key
        if item_o.option:
            item['name'] += ' (%s)'%item_o.option.key

        item['location'] = item_o.location
        item['date'] = None if not item_o.sale_date else item_o.sale_date.strftime('%d.%m.%Y')
        item['id'] = item_o.id

        if not item_o.order_id:
            item['margin']= '%.2f'%item_o.price
        else:
            init_cost, marg = calculate_order_item(item_o)
            item['margin'] = marg

        items.append(item)

    return HttpResponse(json.dumps({'ret_code': 0, 'items': items, \
            'pages_count': pages_count or 1, 'page_num': page_num}),\
            content_type="application/json")

def calculate_income(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    CNT = 15

    if date_from:
        date_from = datetime.strptime(date_from, '%d.%m.%Y')
    if date_to:
        date_to = datetime.strptime(date_to, '%d.%m.%Y')

    orders_items = OrderItem.objects.filter(sale_date__isnull=False)
    if date_from:
        orders_items = orders_items.filter(sale_date__gte=date_from)
    if date_to:
        orders_items = orders_items.filter(sale_date__lte=date_to)

    inc = orders_items.filter(~Q(location='spend'))
    spend = orders_items.filter(location='spend')

    inc_sum = 0
    for item in inc:
        if item.order_id:
            _, marg  = calculate_order_item(item)
            inc_sum += float(marg)
        else:
            inc_sum += item.price

    for item in spend:
        inc_sum -= item.price

    return HttpResponse(json.dumps({'ret_code': 0,\
        'inc_sum': '%.2f'%inc_sum}), content_type="application/json")

def get_json_dict(request, dict_type):
    query = request.GET.get('q', '')
    objects = KeysDict.objects.filter(dict_type=dict_type)
    if query:
        objects = objects.filter(key__icontains=query)

    items = [oi.key for oi in objects]

    return HttpResponse(json.dumps(items), content_type="application/json")


def get_embedebts(request):
    page_num = int(request.GET.get('page_num', 1))
    CNT = 15

    items = EmbeddingDebts.objects.all()
    all_cnt = items.count()
    pages_count = all_cnt / CNT
    if all_cnt % CNT:
        pages_count += 1

    items_o = items.order_by('-em_date')[(page_num-1)*CNT:page_num*CNT]

    items = []
    for item_o in items_o:
        item = {}
        item['description'] = item_o.description
        item['sum'] = item_o.sum
        item['date'] = item_o.em_date.strftime('%d.%m.%Y')
        item['id'] = item_o.id
        item['is_repaid'] = item_o.is_repaid

        items.append(item)

    return HttpResponse(json.dumps({'ret_code': 0, 'items': items, \
            'pages_count': pages_count or 1, 'page_num': page_num}),\
            content_type="application/json")

def get_order_item(request):
    item_id = int(request.GET['item_id'])

    order_item = OrderItem.objects.get(pk=item_id)
    item = {}
    item['brand'] = order_item.brand.key
    item['name'] = order_item.name.key
    item['option'] = '' if not order_item.option else order_item.option.key
    item['cost'] = order_item.cost
    item['price'] = order_item.price
    item['notes'] = order_item.notes

    return HttpResponse(json.dumps({'ret_code': 0, 'item': item}),\
            content_type="application/json")
