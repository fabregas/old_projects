from django.http import HttpResponse
import os
from settings import STATIC_PATH

STATIC_CACHE = {}

def get_data(source):
    data = STATIC_CACHE.get(source, None)

    if not data:
        data = open(os.path.join(STATIC_PATH,source), "rb").read()

        STATIC_CACHE[source] = data

    return data


def get_media(request, source):
    try:
        data = get_data(source)
    except:
        return HttpResponse(status=404)

    if source.endswith(".png"):
        mtype = "image"
    elif source.endswith(".css"):
        mtype = "text/css"
    elif source.endswith(".js"):
        mtype = "text/javascript"
    else:
        mtype = ""

    resp = HttpResponse(data, mimetype=mtype)

    return resp


