from django.http import HttpResponse
import os
from settings import STATIC_PATH

def get_media(request, source):
    try:
        data = open(os.path.join(STATIC_PATH,source), "rb").read()
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

    return HttpResponse(data, mimetype=mtype)


