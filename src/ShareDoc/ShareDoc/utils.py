from __future__ import unicode_literals
from django.http import Http404
import urllib


def url_with_querystring(path, **kwargs):
    return path + '?' + urllib.urlencode(kwargs)


def extract_from_GET(GET, *args):
    extract_list = [GET.get(key, None) for key in args]
    if not all(extract_list):
        raise Http404
    return extract_list
