from __future__ import unicode_literals
# django dependency
from django.http import Http404
from django.http import HttpResponse
from django.views.generic.base import View
# auth dependency
# model
# form
# decorator
# util
# python library
import json
import urllib


class POSTHandler(View):
    """
    Abstration of handling AJAX HTTP POST 
    """
    def __init__(self, *args, **kwargs):
        super(POSTHandler, self).__init__(*args, **kwargs)
        self._registered_handler = []

    def _register_handler(self, handlers):
        self._registered_handler.extend(handlers)

    def _handler_factory(self, request):
        _registered_handler = getattr(self, '_registered_handler')
        for trigger, handler in _registered_handler:
            if trigger in request.POST:
                return handler
        return None
    
    def _handler(self, request, *args, **kwargs):
        handler = self._handler_factory(request)
        return handler(request, *args, **kwargs)


class ApplyConfirmHandler(object):
    """
    handler of the situations that somebody search sth via a form.
    """
    def _apply_confirm_handler(self,
                               request,
                               applier,
                               form_cls,
                               target_set_generator):
        form = form_cls(request.POST)
        if form.is_valid():
            target_set = target_set_generator(form, applier)
            json_data = json.dumps({
                'error': False,
                'data': target_set,
            })
            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form.errors)
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
            json_data = json.dumps({
                'error': error_dict,
            })
            return HttpResponse(json_data, content_type='application/json')


class BasicInfoHandler(object):
    # form process, base on AJAX POST.
    def _basic_info_handler(self, request, target, form_cls, field_name):
        form = form_cls(request.POST)
        if form.is_valid():
            field = form.cleaned_data[field_name]
            setattr(target, field_name, field)
            target.save()
            json_data = json.dumps({
                'error': False,
                'data': {field_name: field},
            })
            return HttpResponse(json_data, content_type='application/json')
        else:
            error_dict = dict(form.errors)
            for key, value in error_dict.items():
                error_dict[key] = "; ".join(value)
            json_data = json.dumps({
                'error': True,
                'data': error_dict,
            })
            return HttpResponse(json_data, content_type='application/json')


def url_with_querystring(path, **kwargs):
    return path + '?' + urllib.urlencode(kwargs)


def extract_from_GET(GET, *args):
    extract_list = [GET.get(key, None) for key in args]
    if not all(extract_list):
        raise Http404
    return extract_list
