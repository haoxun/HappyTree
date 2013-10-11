from __future__ import unicode_literals
from functools import wraps
from django.http import Http404
from django.shortcuts import get_object_or_404
from prototype.utils import recursive_get_attr, exclusive_with_flag_results_Http404

def add_data_from_GET_to_kwargs(*args):
    keys = args[:]
    def _wrap(func):
        @wraps(func)
        def _warp_view(request, *args, **kwargs):
            for key in keys:
                kwargs[key] = request.GET.get(key, None)
            return func(request, *args, **kwargs)
        return _warp_view
    return _wrap

def require_user_in(judge_func, id_name, info):
    # filter method
    def _wrap(func):
        @wraps(func)
        def _wrap_view(request, *args, **kwargs):
            model = info[0]
            flag = info[1]
            attrs = info[2]
            # get ModelInstance
            instance_id = kwargs.get(id_name, None) \
                            if id_name in kwargs \
                                else request.GET.get(id_name, None)
            if instance_id == None:
                raise Http404
            instance_id = int(instance_id)
            model_instance = get_object_or_404(
                                model,
                                id=instance_id)
            # filter
            manager = recursive_get_attr(model_instance, attrs)
            exclusive_with_flag_results_Http404(
                    flag,
                    judge_func(manager, request)
            )
            return func(request, *args, **kwargs) 
        return _wrap_view
    return _wrap






    

