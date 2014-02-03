
import os
import string
import random

from django.http import HttpResponse

from settings import STATIC_PATH

STATIC_CACHE = {}

def generate_sid(letter_count=5):
    return "".join(random.sample(string.letters+string.digits, letter_count))

def get_data(source, static_path=STATIC_PATH):
    data = STATIC_CACHE.get(source, None)

    if not data:
        data = open(os.path.join(static_path, source), "rb").read()

        STATIC_CACHE[source] = data

    return data


def get_media(request, source, m_type=None):
    try:
        data = get_data(source, getattr(request, 'static_path', STATIC_PATH))
    except:
        return HttpResponse(status=404)

    if m_type:
        mtype = m_type
    elif source.endswith(".png"):
        mtype = "image"
    elif source.endswith(".css"):
        mtype = "text/css"
    elif source.endswith(".js"):
        mtype = "text/javascript"
    else:
        mtype = ""

    resp = HttpResponse(data, mimetype=mtype)

    return resp

