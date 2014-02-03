from django import template

register = template.Library()

def get_curindex(menuitem, curitem):
    if menuitem == curitem:
        return u'current'
    return u''


def app_type(type_sid):
    if str(type_sid) == 'native_app':
        return 'WSGI'
    if str(type_sid) == 'shared_lib':
        return 'Library'

def short_datetime(dt):
    return "%.2i:%.2i:%.2i  %.2i.%.2i.%i" % (dt.hour, dt.minute, dt.second, dt.day, dt.month, dt.year)

def long_datetime(dt):
    return "%.2i.%.2i.%i %.2i:%.2i:%.2i.%.3i" % ( dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second,dt.microsecond)

def check_type(value, vtype):
    if not value:
        return 'NULL'

    if int(vtype) == 4:
        return '******'
    return value

def msg_level_image(msg_level):
    msg_level = int(msg_level)

    if msg_level == 0:
        return u'src=/static/level_info.png alt=info'
    elif msg_level == 4:
        return 'src=/static/level_warn.png alt=warn'
    elif msg_level == 2:
        return u'src=/static/level_error.png alt=error'
    else:
        raise Exception('Unsupported message level occured!')

def get_msg_type(msg_id):
    if msg_id == 1:
        return 'input'
    elif msg_id == 2:
        return 'output'
    else:
        return 'error'


def is_checked(status, direction):
    if (direction == 'input' and (status & 2)) or (direction == 'output' and (status & 4)):
        return 'checked=checked'

    return ''


def get_logging_value(status, direction):
    if (direction == 'input' and (status & 2)) or (direction == 'output' and (status & 4)):
        return '1'

    return '0'


register.filter('curindex',get_curindex)
register.filter('app_type',app_type)
register.filter('shortdatetime',short_datetime)
register.filter('longdatetime',long_datetime)
register.filter('check_type',check_type)
register.filter('msg_level_image',msg_level_image)
register.filter('get_msg_type',get_msg_type)
register.filter('is_checked',is_checked)
register.filter('get_logging_value',get_logging_value)
