from django.http import HttpResponse
import os
from settings import STATIC_PATH

STATIC_CACHE = {}

def get_data(source):
    data = STATIC_CACHE.get(source, None)

    if not data:
        for path in STATIC_PATH:
            source_path = os.path.join(path, source)
            if os.path.exists(source_path):
                data = open(source_path, "rb").read()
                break
        else:
            raise Exception('Static file %s is not found at server'%source)

        STATIC_CACHE[source] = data

    return data


def get_media(request, source):
    try:
        data = get_data(source)
    except Exception, err:
        return HttpResponse(err, status=404)

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


