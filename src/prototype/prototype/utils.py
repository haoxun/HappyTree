from __future__ import unicode_literals
import urllib
from django.http import Http404

def url_with_querystring(path, **kwargs):
    return path + '?' + urllib.urlencode(kwargs)

def extract_from_GET(GET, *args):
    extract_list = [GET.get(key, None) for key in args]
    if not all(extract_list):
        raise Http404
    return extract_list

def recursive_get_attr(obj, attrs):
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj

def exclusive_with_flag_results_Http404(p, q):
    p = bool(p)
    q = bool(q)
    if not p == q:
        raise Http404

