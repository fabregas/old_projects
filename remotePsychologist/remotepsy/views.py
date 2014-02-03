# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from auth_views import logout as b_logout, auth_user, get_current_user, is_authenticated, is_authorize
from forms import RegisterForm, RecordCreateForm
import hashlib, uuid
from models import RPUser, RPWorkTime, RPRecord,RPService,RPPayments,RPMessage
from Utilities import MailClient
from datetime import date,datetime, timedelta, time
from django.db import transaction
import liqpay
import logging
import utils
from settings import *
from django.db.models import Min
from django.utils.translation import ugettext as _

MONTHS = {1:_(u'Січень'), 2:_(u'Лютий'), 3:_(u'Березень'), 4:_(u'Квітень'),5:_(u'Травень'),6:_(u'Червень'),7:_(u'Липень'),8:_(u'Серпень'),9:_(u'Вересень'),10:_(u'Жовтень'),11:_(u'Листопад'),12:_(u'Грудень')}

min_money = RPService.objects.filter(is_deleted=0).aggregate(min_money = Min('atom_money'))['min_money']
min_service_time = RPService.objects.filter(is_deleted=0, atom_money=min_money).aggregate(min_time=Min('time_min'))['min_time']

INIT_BALANCE = min_money * (min_service_time / ATOM_TIME)


#payment states
PS_INIT = 0
PS_WAIT = 1
PS_OK   = 2
PS_FAIL = 3


USER_ROLE = 'user'
ADMIN_ROLE = 'admin'

MEM_SESSIONS = {}


def check_mem_sessions():
    to_del_list = []

    for key in MEM_SESSIONS:
        (dt, user) = MEM_SESSIONS[key]

        dr = datetime.now() - dt
        if dr.days > 0:
            to_del_list.append(key)

    for key in to_del_list:
        del MEM_SESSIONS[key]


def init_logger():
    logger = logging.getLogger('remotepsy.liqpay')
    hdlr = logging.FileHandler('/var/log/remotepsy.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    #logger.setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)

    return logger

logger = init_logger()

def inform_message(message, redirect_link='/', yes=None, no=None):
    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link, 'yes':yes, 'no':no})

def authorize(perm, save_path=False):
    def wraper(func):
         def dec_func(request, *args, **kvargs):
             if not is_authenticated(request):
                 return HttpResponseRedirect('/')

             if not is_authorize(request, perm):
                 #return HttpResponseRedirect('/')
                 return inform_message('You are not permissed for this action!')

             ret =  func(request, *args, **kvargs)

             return ret

         return dec_func
    return wraper


def authenticate_user(request):
    form, user = auth_user(request)

    if not user:
        return index(request, form)

    return HttpResponseRedirect('/')

def i18n_service(service, request):
    if request.LANGUAGE_CODE == 'ru':
        service.name = service.name_ru
        service.description = service.description_ru

def index(request, form=None):
    if not form:
        form, user = auth_user(request)
    else:
        user = None

    if not user:
        content = utils.get_data('no_auth_index_content.%s.html'%request.LANGUAGE_CODE)
    elif user.role == 'admin':
        content = utils.get_data('admin_index_content.%s.html'%request.LANGUAGE_CODE)
    else:
        content = utils.get_data('user_index_content.%s.html'%request.LANGUAGE_CODE)

    return render_to_response('index.html',{'form':form, 'user':user,'content':content})

def logout(request):
    b_logout(request)

    return HttpResponseRedirect('/')


def send_activating_letter(email, login, accept_code):
    message = _(u'Доброго дня!\nЦе активаційний лист з сайту %(hostname)s.\nЯкщо ви бажаєте зареєструватись, перейдіть за посиланням http://%(hostname)s/activate_user/%(accept_code)s\n\nЯкщо ви не реєструвались на сайті %(hostname)s, проігноруйте даний лист.') % {'hostname':hostname,'accept_code':accept_code}

    MailClient.sendMail([email], _(u'Лист активації'), message)

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            passwd = form.cleaned_data['passwd']
            name = form.cleaned_data['name']
            #birthday = form.cleaned_data['birthday']
            city = form.cleaned_data['city']
            region = form.cleaned_data['region']
            email = form.cleaned_data['email']

            md5 = hashlib.md5()
            md5.update(passwd.encode('utf8'))
            passwd = md5.hexdigest()

            user = RPUser(login=login, password_md5=passwd, name=name, role='user', region=region, city=city, email=email, balance=INIT_BALANCE)
            accept_code = str(uuid.uuid4())

            #  sessions registration mechanism is not worked on some FF versions :(
            #request.session['unaccepted_user'] = user
            #request.session['accept_code'] = accept_code
            MEM_SESSIONS[accept_code] = (datetime.now(), user)

            send_activating_letter(email, login, accept_code)

            return inform_message(_(u'Ваш аккаунт успішно створено! Інструкцію з активації відправлено Вам на e-mail адресу %(email)s') % {'email': email.encode('utf8')})
    else:
        form = RegisterForm()

    return render_to_response('register.html',{'reg_form':form})


def activate_user(request, accept_code):
    #acc_code = request.session.get('accept_code', None)
    acc_code = MEM_SESSIONS.get(accept_code, None)

    if not acc_code:
        return inform_message(_(u'Інформація про реєстрацію не знайдена! Будь ласка, зареєструйтесь знову...'))

    #user = request.session['unaccepted_user']
    s_datetime, user = acc_code

    user.save()

    #del request.session['unaccepted_user']
    #del request.session['accept_code']
    del MEM_SESSIONS[accept_code]

    act_message = _(u'Вітаємо Вас на сайті психологічної допомоги!\nЯкщо у Вас є питання до психолога, залиште повідомлення на сайті або відправте листа на адресу AnnaSa@i.ua\nСподіємось, що Ви знайдете тут допомогу, яку шукаєте.')
    message = RPMessage(sender=None, binded_user=user, send_datetime=datetime.now(), message=act_message, is_readed=0)

    message.save()

    check_mem_sessions()

    return inform_message(_(u'Вітаємо! Ви успішно зареєстровані. Ви можете увійти у ваш персональний кабінет, використовуючи ваш логін/пароль'))

def change_password_request(request):
    if request.method == 'POST':
        login = request.POST['login']
        new_password = request.POST['new_password']

        if len(new_password.strip()) == 0:
            return inform_message(_(u'Пароль має бути не порожнім!'))

        user = RPUser.objects.filter(login=login)

        if not user:
            return inform_message(_(u'Користувача з логіном %(passwd)s не знайдено на сервері!') %{'passwd':new_password})
        user = user[0]

        accept_code = str(uuid.uuid4())

        md5 = hashlib.md5()
        md5.update(new_password.encode('utf8'))
        passwd = md5.hexdigest()
        user.password_md5 = passwd

        #request.session['accept_code'] = accept_code
        #request.session['unaccepted_user'] = user
        MEM_SESSIONS[accept_code] = (datetime.now(), user)

        message = _(u'Ви забули пароль входу на сайт %(hostname)s.\nДля того, щоб змінити пароль на новий, перейдіть за посиланням http://%(hostname)s/accept_change_password/%(accept_code)s\n\nЯкщо ви не бажаєте змінювати пароль або не зареєстровані на сайті %(hostname)s, будь ласка, проігноруйте даний лист.') % {'hostname':hostname,'accept_code':accept_code}

        MailClient.sendMail([user.email], _(u'Зміна паролю!'), message)

        return inform_message(_(u'Інструкція по зміні паролю вислана Вам на e-mail адресу, вказану при реєстрації'))

    return render_to_response('change_password_form.html',locals())


def accept_change_password(request, accept_code):
    #acc_code = request.session.get('accept_code', None)
    acc_code = MEM_SESSIONS.get(accept_code, None)

    if not acc_code:
        return inform_message(_(u'Інформація про новий пароль не знайдена!\nБудь ласка, спробуйте змінити пароль ще раз'))

    #user = request.session['unaccepted_user']
    dt, user = acc_code

    user.save()

    #del request.session['unaccepted_user']
    #del request.session['accept_code']
    del MEM_SESSIONS[accept_code]

    return inform_message(_(u'Вітаємо! Ви успішно змінили пароль.\nВи можете увійти у ваш персональний кабінет, використовуючи ваш новий пароль'))


@authorize(USER_ROLE)
def get_month_calendar(request):
    class Day:
        def __init__(self, cdate=None, user=None):
            if not cdate:
                self.num = ''
                self.is_current = False
                self.is_active = False
                self.is_recorded = False
                return

            self.num = cdate.day

            current = date.today()

            if current == cdate:
                self.is_current = True

            if cdate < current:
                self.is_active = False
            else:
                nextday = cdate + timedelta(1)
                work_ranges = RPWorkTime.objects.filter(start_worktime__gt=cdate, stop_worktime__lt=nextday)
                record_ranges = len(RPRecord.objects.filter(start_datetime__gt=cdate, stop_datetime__lt=nextday, user=user))
                if work_ranges:
                    self.is_active = True
                if record_ranges:
                    self.is_recorded = True


    class Month:
        def __init__(self, name, num, year):
            self.name = name
            self.weeks = []
            self.num = num
            self.year = year

    cur_date = request.session.get('DATE',None)
    user = get_current_user(request)

    if not cur_date:
        cur_date = date.today()
        cur_date = date(cur_date.year, cur_date.month, 1)
        request.session['DATE'] = cur_date

    month = Month(MONTHS[cur_date.month], cur_date.month, cur_date.year)

    weeks = []
    start_idx = cur_date.weekday()
    week = [Day() for i in xrange(start_idx)]
    cur_month = cur_date.month
    while cur_month == cur_date.month:
        week.append(Day(cur_date, user))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur_date = cur_date + timedelta(1)

    week += [Day() for i in xrange(7-len(week))]
    weeks.append(week)

    month.weeks = weeks

    return render_to_response('month_calendar.html',locals())

def get_next_month(request):
    cur_date = request.session.get('DATE',None)

    if not cur_date:
        return HttpResponseRedirect('/find_record_time')

    new_date = timedelta(31) + cur_date
    new_date = date(new_date.year, new_date.month, 1)
    request.session['DATE'] = new_date

    return HttpResponseRedirect('/find_record_time')

def get_prev_month(request):
    cur_date = request.session.get('DATE',None)

    if not cur_date:
        return HttpResponseRedirect('/find_record_time')

    new_date = cur_date - timedelta(1)
    new_date = date(new_date.year, new_date.month, 1)
    request.session['DATE'] = new_date

    return HttpResponseRedirect('/find_record_time')


def _get_res_range(range_1, range_2):
    if range_1[1] <= range_2[0] or range_2[1] <= range_1[0]:
        return None

    rr = [None,None]
    if range_1[0] < range_2[0]:
        rr[0] = range_2[0]
    else:
        rr[0] = range_1[0]

    if range_1[1] > range_2[1]:
        rr[1] = range_2[1]
    else:
        rr[1] = range_1[1]

    return rr


def _get_free_range(range1, range2):
    rr = []

    if (range1[0] >= range2[0]) and (range1[1] <= range2[1]):
        return None

    if (range1[1] <= range2[0]) or (range1[0] >= range2[1]):
        return []

    if range1[0] < range2[0]:
        if range1[1] < range2[0]:
            return rr
        rr.append((range1[0], range2[0]))

    if range2[1] < range1[1]:
        if range2[1] < range1[0] or range2[1] > range1[1]:
            return rr
        rr.append((range2[1], range1[1]))

    return rr

def _get_time_delta(time1, time2):
    delta = datetime(1,1,1,time1.hour,time1.minute) - datetime(1,1,1,time2.hour,time2.minute)

    return delta.seconds / 60


class Hour:
    def __init__(self, h, f=0):
        self.hour = h
        self.ranges = []
        self.free = f
        self.parts = []

    def append(self, r):
        self.ranges.append(r)

    def calculate_free(self):
        for part in range(60/ATOM_TIME):
            free = False
            cur_range = (time(self.hour, part*ATOM_TIME), time(self.hour, (part+1)*ATOM_TIME-1))

            if self.ranges is None:
                self.ranges = []

            for r in self.ranges:
                if len(self.ranges) > 2:
                    break

                ret = _get_res_range(r,(time(self.hour, part*ATOM_TIME), time(self.hour, (part+1)*ATOM_TIME-1)))

                if ret and (ret[0] == cur_range[0]) and (ret[1] == cur_range[1]):
                    free = True
                    break


            if not self.ranges:
                free = False

            self.parts.append(Hour('%.2i:%.2i'%(self.hour,part*ATOM_TIME), free))

        if not self.ranges:
            self.ranges = []
            return
        for r in self.ranges:
            self.free += _get_time_delta(r[1],r[0])



    def __repr__(self):
        return str (self.ranges)


def _get_free_ranges(day):
    nextday = day + timedelta(1)

    work_ranges = RPWorkTime.objects.filter(start_worktime__gt=day, stop_worktime__lt=nextday).order_by('start_worktime')

    record_ranges = RPRecord.objects.filter(start_datetime__gt=day, stop_datetime__lt=nextday).order_by('start_datetime')

    if day == datetime.today().date():
        fake_rec = RPRecord()
        d = datetime.now()
        fake_rec.start_datetime = datetime(d.year, d.month, d.day, 0,0)
        fake_rec.stop_datetime = datetime.now() + timedelta(0, IDENT_RECORD_TIME*3600,0)
        if fake_rec.start_datetime.day != fake_rec.stop_datetime:
            fake_rec.stop_datetime =  datetime(d.year, d.month, d.day,23,59)

        record_ranges = [r for r in record_ranges]
        record_ranges.append(fake_rec)

    if not work_ranges:
        return {}

    ranges = {}
    start_hour = work_ranges[0].start_worktime.hour
    stop_hour = work_ranges[len(work_ranges)-1].stop_worktime.hour

    if stop_hour != 23:
        stop_hour += 1

    ret_hours = {}
    for hour in range(start_hour, stop_hour):
        h_range = [time(hour,0,0,0),time(hour+1,0,0,0)]
        ret_hours[hour] = []
        for wrange in work_ranges:
            rr = _get_res_range([wrange.start_worktime.time(), wrange.stop_worktime.time()], h_range)
            if rr:
                ret_hours[hour].append( (rr[0], rr[1]) )

    hours = {}
    for hour in ret_hours:
        h = Hour(hour)
        for rrange in record_ranges:
            for hrange in ret_hours[hour]:
                rr = _get_free_range(hrange, [rrange.start_datetime.time(), rrange.stop_datetime.time()])

                if rr is None:
                    h.ranges = None
                    break

                for r in rr:
                    h.append( r )

        if h.ranges is None:
            pass
        elif not h.ranges:
            for r in ret_hours[hour]:
                h.append(r)

        hours[hour] = h

    for h in hours:
        c_hour = hours[h]
        #if c_hour.ranges and len(c_hour.ranges) > 1:
        #    hour = hours[h+1]
        #    if hour.ranges and hour.ranges[0][0].minute < 15:
        #        pass
        #    else:
        #        c_hour.ranges = []
        c_hour.calculate_free()

    return hours


@authorize(USER_ROLE)
def get_day_calendar(request, day_str):
    day,month,year =  day_str.split('/')
    day,month,year = int(day), int(month), int(year)

    today = date(year, month, day)


    request.session['selected_day'] = today

    day = '%s %i, %s' % ( MONTHS[month], day, year)

    hours_dict = _get_free_ranges(today)
    keys = hours_dict.keys()
    keys.sort()
    hours = [hours_dict[key] for key in keys]

    user = get_current_user(request)


    return render_to_response('day_calendar.html', locals())

@authorize(USER_ROLE)
@transaction.commit_manually
def record_form(request, hour):
    day = request.session['selected_day']
    user = get_current_user(request)

    if request.method == 'POST':
        form = RecordCreateForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            record = RPRecord()
            record.user = get_current_user(request)
            service = RPService.objects.get(id=int(cd['service']))

            record.service = service

            h,m = cd['start_time'].split(':')
            s_date = datetime(day.year, day.month, day.day, int(h), int(m))
            record.start_datetime = s_date

            h,m = cd['stop_time'].split(':')
            s_date = datetime(day.year, day.month, day.day, int(h), int(m))
            record.stop_datetime = s_date
            record.comment = cd['comment']

            #check duble-record
            finded = RPRecord.objects.filter(start_datetime__gt=datetime(day.year, day.month, day.day,0,0), stop_datetime__lt=datetime(day.year, day.month, day.day,23,59), user=record.user)
            if finded:
                st_dt = finded[0].start_datetime
                en_dt = finded[0].stop_datetime
                start_time = '%.02i:%.02i'%(st_dt.hour, st_dt.minute)
                stop_time = '%.02i:%.02i'%(en_dt.hour, en_dt.minute)
                return inform_message(_(u'Ви вже записані на цей день з %(start_time)s до %(stop_time)s. Якщо бажаєте змінити час запису, то відмініть ваш прийом, а потім запишіться на інший час') % {'start_time': unicode(start_time), 'stop_time' : unicode(stop_time)}, redirect_link='/my_records/')


            res = record.stop_datetime - record.start_datetime
            cost = ((res.seconds/60.0) / ATOM_TIME) * service.atom_money

            #check current user balance
            if user.balance < cost:
                return inform_message(_(u'У вас недостатньо коштів для запису. Поповніть, будь ласка, свій рахунок '), '/my_balance')

            record.user.balance -= cost

            try:
                record.user.save()
                record.save()
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()

            return inform_message(_(u'Ви успішно записались на прийом з %(start_time)s до %(stop_time)s. Вартість послуги - %(cost)i гривень') % {'start_time': unicode(cd['start_time']), 'stop_time': unicode(cd['stop_time']), 'cost': int(cost)}, redirect_link='/my_records/')

        raise Exception('Record form data is not valid')

    hours = _get_free_ranges(day)

    hour = int(hour)
    hour_obj = hours.get(hour, None)

    if not hour_obj:
        return render_to_response('record_form.html',{})

    if len(hour_obj.ranges) > 1:
        start_time = hour_obj.ranges[-1][0]
        start_time_end = hour_obj.ranges[-1][1]
    else:
        start_time = hour_obj.ranges[0][0]
        start_time_end = hour_obj.ranges[0][1]

    minute = (((start_time.minute-1) / ATOM_TIME) + 1)*ATOM_TIME
    if start_time.hour == start_time_end.hour:
        end_minute = (((start_time_end.minute-1) / ATOM_TIME) + 1)*ATOM_TIME
    else:
        end_minute = 60

    start_times = []
    for c_min in range(minute, end_minute, ATOM_TIME):
        start_times.append('%.2i:%.2i'%(start_time.hour, c_min))

    services = RPService.objects.all()
    for service in services:
        service.atom_money *= 60/ATOM_TIME
        i18n_service(service, request)

    day_path = '%s/%s/%s'%(day.day, day.month, day.year)
    return render_to_response('record_form.html',locals())

@authorize(USER_ROLE)
def get_record_endtime(request):
    service_id = request.REQUEST['service_id']
    start_time = request.REQUEST['start_time']

    h,m = start_time.split(":")

    start_time = time(int(h), int(m))

    service = RPService.objects.filter(id=service_id)

    if not service:
        raise Exception('Service is not found!')

    max_time = service[0].time_max
    min_time = service[0].time_min

    day = request.session['selected_day']

    hours = _get_free_ranges(day) #TODO: may be caching ranges?!

    for h in range(start_time.hour+1,24):
        h_range = hours.get(h, None)
        if h_range is None or h_range.ranges == []:
            stop_time = hours.get(h-1).ranges[0][1]
            break

        h_range = h_range.ranges[0]
        if h_range[0].minute > ATOM_TIME:
            stop_time = hours.get(h-1).ranges[-1][1]
            break
        if h_range[1].minute < 59:
            stop_time = h_range[1]
            break
    diff_time = _get_time_delta(stop_time, start_time)

    if diff_time < min_time:
        return HttpResponse('')
        #raise Exception('Time range is lower than minimum (%i)'%min_time)

    d = datetime(1,1,1,start_time.hour,start_time.minute) + timedelta(0, min_time*60, 0)
    stop_time_start = d.time()

    diff_time = _get_time_delta(stop_time, start_time)
    if diff_time > max_time:
        d = datetime(1,1,1,start_time.hour, start_time.minute) + timedelta(0, max_time*60, 0)
        stop_time = d.time()
        diff_time = max_time

    stop_times = []
    iters = (diff_time - min_time) / ATOM_TIME + 1
    cur_time = datetime(1,1,1, stop_time_start.hour, stop_time_start.minute)
    for i in xrange(iters):
        stop_times.append('%.2i:%.2i'%(cur_time.hour, cur_time.minute))
        cur_time += timedelta(0, ATOM_TIME*60, 0)

    return HttpResponse(','.join(stop_times))


@authorize(USER_ROLE)
def get_user_records(request):
    user = get_current_user(request)

    records = RPRecord.objects.filter(user=user).order_by('-start_datetime')

    now = datetime.now()
    for record in records:
        if record.start_datetime <= now:
            record.is_past = True
        else:
            record.is_past = False

    user = get_current_user(request)
    return render_to_response('user_records_form.html',locals())


@transaction.commit_manually
def cancel_record(request, record_id, is_admin=False):
    record = RPRecord.objects.get(id=record_id)

    if is_admin:
        user = record.user
    else:
        user = get_current_user(request)

    if not record:
        raise Exception("Record with ID %s is not found in database!"%record_id)

    if record.user != user:
        raise Exception("It's not your record!!!")

    if not is_admin:
        if record.start_datetime < datetime.now():
            return inform_message(_(u'Не можна відмінити прийом, який вже пройшов (або під час його)!'), '/my_records')

        diff = record.start_datetime - datetime.now()

        if diff.days == 0 and (diff.seconds/60.0 < MIN_CANCEL_TIME):
            return inform_message(_(u'Відмінити прийом можна не менше ніж за %(min_time)i хвилин!')% {'min_time':MIN_CANCEL_TIME}, '/my_records')

    res = record.stop_datetime - record.start_datetime
    cost = ((res.seconds/60.0) / ATOM_TIME) * record.service.atom_money

    #check current user balance
    user.balance += cost

    try:
        record.delete()
        user.save()
    except Exception, err:
        transaction.rollback()
        raise err
    else:
        transaction.commit()

    return inform_message(_(u'Ви успішно відмінили прийом'), '/my_records')

#--------- messages --------------------------------

@authorize(USER_ROLE)
def get_messages(request):
    user = get_current_user(request)

    is_outbox = request.REQUEST.get('is_outbox',None)
    full_message_id = request.REQUEST.get('msg_id',None)

    if is_outbox:
        messages = RPMessage.objects.filter(sender=user).order_by('-send_datetime')
    else:
        messages = RPMessage.objects.filter(binded_user=user).order_by('-send_datetime')

    for message in messages:
        if full_message_id and int(full_message_id) == message.id:
            if (not message.is_readed) and (not is_outbox):
                message.is_readed = 1
                message.save()
            continue

        if len(message.message) > 20:
            message.message = message.message.split('\n')[0][0:20]+'  ...'

    messages = [msg for msg in messages]
    if len(messages) < 20:
        for i in xrange(20-len(messages)):
            messages.append(RPMessage())

    return render_to_response('user_messages.html',locals())



@authorize(USER_ROLE)
def send_message(request):
    if request.method != 'POST':
        raise Exception('POST expected for send_message')

    if not request.POST.has_key('message'):
        raise Exception('message is not found at POST data')

    user = get_current_user(request)
    message = RPMessage(sender=user, binded_user=None, send_datetime=datetime.now(), message=request.POST['message'], is_readed=0)

    message.save()
    return HttpResponse('')

@authorize(USER_ROLE)
def services_description(request):
    user = get_current_user(request)

    services = RPService.objects.filter(is_deleted=0)

    part = 60.0 / ATOM_TIME
    for service in services:
        i18n_service(service, request)
        service.hour_money = int( service.atom_money * part )

    return render_to_response('services_description.html',locals())

########## LiqPay ###################################

@authorize(USER_ROLE)
def get_liqpay_form(request):
    user = get_current_user(request)
    money_count = request.REQUEST['money']

    money_count = float(money_count)

    l = liqpay.Liqpay(MERCHANT_ID, SIGNATURE)

    #balance = l.get_ballances() # balance['UAH']
    payment = RPPayments(user=user, money=money_count, transaction_start=datetime.now(),transaction_end=None, status=PS_INIT, phone_number='')
    payment.save()

    xml = l.build_merchant_xml(order_id=payment.id, amount=money_count, currency='UAH', description='Psychologist service', pay_way='card', default_phone='', result_url='http://%s/liqpay_redirect/'%hostname, server_url='http://%s/liqpay_response/'%hostname)
    logger.debug('LIQPAY REQUEST:\n%s'%xml.xml)

    enc_xml = xml.encoded_xml
    signature = xml.encoded_signature

    return HttpResponse('%s,%s'%(enc_xml, signature))

def liqpay_redirect(request):
    return inform_message(_(u'Ваш платіж успішно відправлений. Щойно банк підтвердить переказ коштів, вони будуть нараховані на ваш рахунок'), '/my_balance')


def apply_payment(response):
    try:
        payment_id = response.order_id
        payment = RPPayments.objects.get(id=payment_id)
        user = payment.user

        if not payment:
            raise Exception( 'IT IS CRITICAL ERROR! Payment is not found in database, but liqPay sent response. Order ID: %s'%response.order_id)

        if response.status == 'success':
            status = PS_OK
        elif response.status == 'failure':
            status = PS_FAIL
        elif response.status == 'wait_secure':
            status = PS_WAIT
        else:
            status = PS_FAIL
            logger.error('LiqPay send payment status as "%s" but it is not expected!'%status)

        if status != PS_WAIT:
            payment.transaction_end = datetime.now()

        payment.status = status

        if hasattr(response, 'phone_number'):
            payment.phone_number = response.sender_phone

        payment.money = response.amount

        if payment.status == PS_OK:
            user.balance += payment.money
    except Exception, err:
        logger.error('apply_payment error: %s'%(err))
    finally:
        try:
            user.save()
            payment.save()
        except Exception, err:
            logger.error('Error while saving user balance!!! User balance in this point must be %s'%user.balance)
            raise err


def check_payment(payment):
    l = liqpay.Liqpay(MERCHANT_ID, SIGNATURE)

    tr_info = None
    try:
        tr_info = l.get_transaction(order_id=payment.id)

        logger.debug('LIQPAY TRANSACTION INFO:\n' +
            'amount = %s\n'% tr_info.amount +
            'description = %s\n'% tr_info.description +
            'order_id = %s\n'% tr_info.order_id +
            'status = %s\n'% tr_info.status)


        apply_payment(tr_info)
    except liqpay.LiqpayOperationError, err:
        logger.error('check_transactions operational error for order_id = %s: %s'%(payment.id,err))

        payment.status = PS_FAIL
        payment.transaction_end = datetime.now()
        payment.save()
    except Exception, err:
        logger.error('check_transactions error for order_id = %s: %s'%(payment.id,err))
        return

    if tr_info:
        return tr_info.status

    return 'failure'

def check_transactions(check_status):
    l = liqpay.Liqpay(MERCHANT_ID, SIGNATURE)

    if check_status == 'init':
        st = PS_INIT
    else:
        st = PS_WAIT

    for payment in RPPayments.objects.filter(status=st):
        try:
            tr_info = l.get_transaction(order_id=payment.id)

            logger.debug('LIQPAY TRANSACTION INFO:\n' +
                'amount = %s\n'% tr_info.amount +
                'description = %s\n'% tr_info.description +
                'order_id = %s\n'% tr_info.order_id +
                'status = %s\n'% tr_info.status)

            if tr_info.status == 'wait_secure':
                continue

            apply_payment(tr_info)
        except liqpay.LiqpayOperationError, err:
            logger.error('check_transactions operational error for order_id = %s: %s'%(payment.id,err))

            payment.status = PS_FAIL
            payment.transaction_end = datetime.now()
            payment.save()
        except Exception, err:
            logger.error('check_transactions error for order_id = %s: %s'%(payment.id,err))

def liqpay_response(request):
    if request.method != 'POST':
        raise Exception('POST method expected for /liqpay_response')

    payment = None

    try:
        op_xml = request.POST['operation_xml']
        signature = request.POST['signature']

        l = liqpay.Liqpay(MERCHANT_ID, SIGNATURE)
        response = l.parse_merchant_response_xml(op_xml, signature)
        r = response

        logger.debug('LIQPAY RESPONSE: \n'+
            '\tsender_phone: %s\n'% r.sender_phone +
            '\tpay_details: %s\n'% r.pay_details +
            '\ttransaction_id: %s\n'% r.transaction_id +
            '\tamount: %s\n'% r.amount +
            '\tstatus: %s\n'% r.status +
            '\tcode: %s\n'% r.code +
            '\tdescription: %s\n'% r.description)

        apply_payment(response)
    except Exception, err:
        logger.error(str(err))

    return HttpResponse('')


@authorize(USER_ROLE)
def user_balance(request):
    user = get_current_user(request)

    payments = RPPayments.objects.filter(status__in=[PS_OK,PS_WAIT], user=user).order_by('-transaction_end')

    return render_to_response('user_balance.html',locals())

def get_liqpay_balance():
    l = liqpay.Liqpay(MERCHANT_ID, SIGNATURE)

    balances = l.get_ballances()

    return balances['UAH']

#####################################################


@authorize(ADMIN_ROLE)
def manage_worktime(request):
    class Day:
        def __init__(self, cdate=None):
            self.is_active = False
            self.is_recorded = False

            if not cdate:
                self.num = ''
                self.is_current = False
                self.is_past = False
                return

            self.num = cdate.day

            current = date.today()

            if current == cdate:
                self.is_current = True

            if cdate < current:
                self.is_past = True
            else:
                nextday = cdate + timedelta(1)
                work_ranges = len(RPWorkTime.objects.filter(start_worktime__gt=cdate, stop_worktime__lt=nextday))
                record_ranges = len(RPRecord.objects.filter(start_datetime__gt=cdate, stop_datetime__lt=nextday))
                if work_ranges:
                    self.is_active = True
                if record_ranges:
                    self.is_recorded = True



    class Month:
        def __init__(self, name, num, year):
            self.name = name
            self.weeks = []
            self.num = num
            self.year = year

    cur_date = request.session.get('DATE',None)
    if not cur_date:
        cur_date = date.today()
        cur_date = date(cur_date.year, cur_date.month, 1)
        request.session['DATE'] = cur_date

    month = Month(MONTHS[cur_date.month], cur_date.month, cur_date.year)

    weeks = []
    start_idx = cur_date.weekday()
    week = [Day() for i in xrange(start_idx)]
    cur_month = cur_date.month
    while cur_month == cur_date.month:
        week.append(Day(cur_date))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur_date = cur_date + timedelta(1)

    week += [Day() for i in xrange(7-len(week))]
    weeks.append(week)

    month.weeks = weeks
    user = get_current_user(request)

    return render_to_response('admin_calendar.html',locals())

def get_next_manage_month(request):
    cur_date = request.session.get('DATE',None)

    if not cur_date:
        return HttpResponseRedirect('/manage_worktime')

    new_date = timedelta(31) + cur_date
    new_date = date(new_date.year, new_date.month, 1)
    request.session['DATE'] = new_date

    return HttpResponseRedirect('/manage_worktime')

def get_prev_manage_month(request):
    cur_date = request.session.get('DATE',None)

    if not cur_date:
        return HttpResponseRedirect('/manage_worktime')

    new_date = cur_date - timedelta(1)
    new_date = date(new_date.year, new_date.month, 1)
    request.session['DATE'] = new_date

    return HttpResponseRedirect('/manage_worktime')


def check_saving_ranges(ranges):
    if len(ranges) == 1:
        return True

    wrange = ranges[0]
    ranges = ranges[1:]

    for l_range in ranges:
        if ((wrange[0] >= l_range[0]) and (wrange[0] < l_range[1])) or ((l_range[0] >= wrange[0]) and (l_range[0] < wrange[1])):
            return False

    return check_saving_ranges(ranges)

@authorize(ADMIN_ROLE)
def manage_day_calendar(request, day_str):
    day,month,year =  day_str.split('/')
    day,month,year = int(day), int(month), int(year)

    today = datetime(year, month, day)

    if today < datetime.today():
        is_past_date = True

    request.session['selected_day'] = today

    day = '%s %i, %s' % ( MONTHS[month], day, year)

    nextday = today + timedelta(1)
    work_ranges = RPWorkTime.objects.filter(start_worktime__gt=today, stop_worktime__lt=nextday).order_by('start_worktime')

    record_ranges = RPRecord.objects.filter(start_datetime__gt=today, stop_datetime__lt=nextday).order_by('start_datetime')

    user = get_current_user(request)

    return render_to_response('manage_day.html', locals())

def get_subranges(work_range, record):
    print work_range, record
    ret = []

    if work_range[1] <= record[0] or record[1] <= work_range[0]:
        return [record]

    if work_range[0] > record[0]:
        ret.append((record[0], work_range[0]))

    if work_range[1] < record[1]:
        ret.append((work_range[1], record[1]))

    return ret


def check_records(wranges, rranges):
    for record in rranges:
        record = [(record.start_datetime, record.stop_datetime)]

        for work_range in wranges:
            new_rec = []
            for r_range in record:
                new_rec += get_subranges(work_range, r_range)

            record = new_rec
            if not record:
                break

        if record:
            return False

    return True

@authorize(ADMIN_ROLE)
@transaction.commit_manually
def save_day_calendar(request):
    if request.method == 'POST':
        today = request.session['selected_day']
        nextday = today + timedelta(1)

        wranges = []
        for key in request.POST:
            time_range = request.POST[key]

            start_time,stop_time = time_range.split('-')
            start_time = start_time.split(':')
            start_time = datetime(today.year, today.month, today.day, int(start_time[0]), int(start_time[1]))
            stop_time = stop_time.split(':')
            stop_time = datetime(today.year, today.month, today.day, int(stop_time[0]), int(stop_time[1]))

            wranges.append((start_time, stop_time))

        if wranges and not check_saving_ranges(wranges):
            return inform_message(_(u'Діапазони часу не мають перетинатись! Будь ласка, оберіть діапазони часу коректно'), '/manage_day/%s/%s/%s'%(today.day, today.month,today.year))

        record_ranges = RPRecord.objects.filter(start_datetime__gt=today, stop_datetime__lt=nextday).order_by('start_datetime')
        if not check_records(wranges, record_ranges):
            return inform_message(_(u'У вас запланований пройом в той час, який Ви відзначили як не робочий! Будь ласка, змініть діапазон робочoго часу або відмініть прийом'), '/manage_day/%s/%s/%s'%(today.day, today.month,today.year))

        try:
            RPWorkTime.objects.filter(start_worktime__gt=today, stop_worktime__lt=nextday).delete()

            for w_time in wranges:
                wt = RPWorkTime(start_worktime=w_time[0], stop_worktime=w_time[1])
                wt.save()
        except Exception, err:
            transaction.rollback()
            raise err
        else:
            transaction.commit()

        return inform_message(_(u'Ви успішно змінили діапазони робочих годин'), '/manage_worktime')
    else:
        today = datetime.today()

        return manage_day_calendar(request, '%s/%s/%s'%(today.day, today.month, today.year))



@authorize(ADMIN_ROLE)
def manage_record(request, record_id):
    user = get_current_user(request)
    record = RPRecord.objects.get(id=record_id)

    return render_to_response('manage_record.html', locals())


@authorize(ADMIN_ROLE)
def admin_cancel_record(request, record_id):
    record = RPRecord.objects.get(id=record_id)
    user = get_current_user(request)

    day = '%s/%s/%s'%(record.start_datetime.day, record.start_datetime.month, record.start_datetime.year)

    if request.method == 'POST':
        message = request.POST['message']
        if message.strip() == '':
            return inform_message(_(u'Ви не ввели причину відміни прийому'), '/admin_cancel_record/%s'%record_id)

        message = _(u'Шановний %(name)s, Ваш прийом %(day).02i.%(month).02i.%(year)i було відмінено.\nПричина: %(message)s.\nБудь ласка, виберіть інший час прийому.\nСподіваємося на розуміння.') % {'name':record.user.name, 'day':record.start_datetime.day, 'month':record.start_datetime.month, 'year':record.start_datetime.year, 'message': message}

        try:
            cancel_record(request, record_id, is_admin=True)
        except Exception,err:
            raise err
        else:
            message = RPMessage(sender=user, binded_user=record.user, send_datetime=datetime.now(), message=message, is_readed=0)
            message.save()
        return inform_message(_(u'Ви успішно відмінили прийом'), '/manage_day/%s'%day)


    return render_to_response('admin_cancel_record.html', locals())

@authorize(ADMIN_ROLE)
def cancel_past_record(request, record_id):
    record = RPRecord.objects.get(id=record_id)
    message = _(u'Шановний %(name)s, На Ваш віртуальний рахунок була повернена оплата за прийом %(day).02i.%(month).02i%(year)i.\n') % {'name':record.user.name, 'day':record.start_datetime.day, 'month':record.start_datetime.month, 'year':record.start_datetime.year}
    user = get_current_user(request)
    day = '%s/%s/%s'%(record.start_datetime.day, record.start_datetime.month, record.start_datetime.year)

    try:
        cancel_record(request, record_id, is_admin=True)
    except Exception,err:
        raise err
    else:
        message = RPMessage(sender=user, binded_user=record.user, send_datetime=datetime.now(), message=message, is_readed=0)
        message.save()

    return inform_message(_(u'Ви успішно повернули кошти клієнту.\nІнформація про даний прийом видалена з системи'), '/manage_day/%s'%day)


@authorize(ADMIN_ROLE)
def manage_users(request):
    users = RPUser.objects.filter(role='user')
    user = get_current_user(request)

    return render_to_response('manage_users.html', locals())

@authorize(ADMIN_ROLE)
def manage_user(request, user_id):
    m_user = RPUser.objects.get(id=user_id)
    user = get_current_user(request)

    if request.method == 'POST':
        message = request.POST['message']
        if message.strip() == '':
            return inform_message(_(u'Ви не ввели текст повідомлення'), '/manage_user/%s'%user_id)

        message = RPMessage(sender=user, binded_user=m_user, send_datetime=datetime.now(), message=message, is_readed=0)
        message.save()
        return inform_message(_(u'Повідомлення відправлено успішно'), '/manage_user/%s'%user_id)

    payments = RPPayments.objects.filter(user=m_user).order_by('-transaction_end')[:100] #FIXME
    for payment in payments:
        if payment.status == PS_OK:
            payment.status = _(u'Успішно')
        elif payment.status == PS_FAIL:
            payment.status = _(u'Помилка')

    records = RPRecord.objects.filter(user=m_user).order_by('-stop_datetime')[:100] #FIXME

    return render_to_response('manage_user.html', locals())

@authorize(ADMIN_ROLE)
def check_payment_state(request, payment_id):
    payment = RPPayments.objects.get(id=payment_id)

    status = check_payment(payment)

    if status == 'success':
        status = _(u'Успішно проведено')
    elif status == 'failure':
        status = _(u'Платіж не проведено')
    elif status == 'wait_secure':
        status = _(u'Очікує підтвердження')

    if status:
        return inform_message(_(u'Статус платежу: %(status)s')%{'status':status}, '/manage_user/%s'%payment.user.id)
    else:
        return inform_message(_(u'Помилка перевірки статусу! Спробуйте пізніше або зверніться до розробників сайту'), '/manage_user/%s'%payment.user.id)


@authorize(ADMIN_ROLE)
def manage_messages(request):
    user = get_current_user(request)
    full_message_id = request.REQUEST.get('msg_id',None)
    is_outbox = request.REQUEST.get('is_outbox',None)

    if is_outbox:
        messages = RPMessage.objects.filter(sender=user).order_by('-send_datetime')[0:100]
    else:
        messages = RPMessage.objects.filter(binded_user=None).order_by('-send_datetime')[0:100]

    for message in messages:
        if full_message_id and int(full_message_id) == message.id:
            if (not message.is_readed) and (not is_outbox):
                message.is_readed = 1
                message.save()
            continue

        if len(message.message) > 20:
            message.message = message.message.split('\n')[0][0:20]+'  ...'


    return render_to_response('manage_messages.html', locals())

@authorize(ADMIN_ROLE)
def admin_balance(request):
    user = get_current_user(request)

    balance = get_liqpay_balance()

    return render_to_response('admin_balance.html', locals())


@authorize(ADMIN_ROLE)
def admin_services(request):
    user = get_current_user(request)

    services = RPService.objects.filter(is_deleted=0)

    return render_to_response('admin_services.html', locals())


@authorize(ADMIN_ROLE)
def manage_service(request, service_id):
    user = get_current_user(request)

    if service_id:
        service_id = int(service_id)

    if request.method == 'POST':
        name = request.POST['name'].strip()
        name_ru = request.POST['name_ru'].strip()
        time_min = int(request.POST['time_min'])
        time_max = int(request.POST['time_max'])
        atom_money = int(request.POST['atom_money'])
        description = request.POST['description'].strip()
        description_ru = request.POST['description_ru'].strip()

        if not name:
            raise Exception('service name should be not empty')

        if atom_money <= 0:
            raise Exception('service atom_money should be greater then 0')

        if time_min > time_max:
            raise Exception('time_max should be greater or equal then time_min')

        if service_id:
            service = RPService.objects.get(id=int(service_id))
        else:
            service = RPService(name='', time_min=0, time_max=0, atom_money=0, description='', name_ru='', description_ru='')

        service.name = name
        service.time_min = time_min
        service.time_max = time_max
        service.atom_money = atom_money
        service.description = description
        service.name_ru = name_ru
        service.description_ru = description_ru

        service.save()

        return inform_message(_(u'Інформація про послугу успішно збережена!'), '/admin_services')


    if service_id:
        service = RPService.objects.get(id=service_id)
    else:
        service = RPService(name='', time_min=0, time_max=0, atom_money=0, description='', name_ru='', description_ru='')

    ##################################
    #TODO: rewrite this fucking code to javascript
    class Time:
        def __init__(self, num, descr):
            self.num = num
            self.descr = descr

    time_min_list = [Time(30, _(u'30 хвилин')), Time(45, _(u'45 хвилин')), Time(60, _(u'1 година'))]
    tmp = []
    for time in time_min_list:
        if service.time_min == time.num:
            tmp.insert(0, time)
        else:
            tmp.append(time)
    service.time_min = tmp

    time_max_list = [Time(30, _(u'30 хвилин')), Time(45, _(u'45 хвилин')), Time(60, _(u'1 година')), Time(75, _(u'1 година 15 хвилин')), Time(90, _(u'1 година 30 хвилин')), Time(105, _(u'1 година 45 хвилин')), Time(120, _(u'2 години'))]
    tmp = []
    for time in time_max_list:
        if service.time_max == time.num:
            tmp.insert(0, time)
        else:
            tmp.append(time)
    service.time_max = tmp
    ##################################

    return render_to_response('manage_service.html', locals())

@authorize(ADMIN_ROLE)
def delete_service(request, service_id):
    user = get_current_user(request)

    service = RPService.objects.get(id=int(service_id))

    records = RPRecord.objects.filter(stop_datetime__gt=datetime.now(), service=service)

    if records:
        return inform_message(_(u'Видалення послуги неможливе тому, що є заплановані записи на дану послугу!'), '/admin_services')


    service.is_deleted=1
    service.save()

    return inform_message(_(u'Ви успішно видалили послугу!'), '/admin_services')
