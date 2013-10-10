# Create your views here.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

@login_required
def show_root(request):
    return render(request, 'user_status/root.html', {'user': request.user})

@login_required
def logout_user(request):
    logout(request)
    return redirect('login_page')


def show_models(request):
    import cgi
    from django.utils.safestring import mark_safe
    from django.contrib.auth.models import User, Group
    from user_status.models import UserInfo
    from group_info.models import GroupInfo
    from project_info.models import ProjectInfo
    def wrap_sth(sth, foot=None):
        if foot == None:
            foot = sth
        def _wrap(target):
            return "<{0}>{1}</{2}>".format(sth, unicode(target), foot)
        return _wrap
    model_set = [User, Group, UserInfo, GroupInfo, ProjectInfo]
    printed_models = []
    for model in model_set:
        field_set = model._meta.get_all_field_names()
        printed_objects = []
        for instance in model.objects.all():
            printed_instance = []
            for field in field_set:
                try:
                    val = getattr(instance, field)
                except:
                    val = None
                # deal with many-to-many, many-to-one situation
                if val.__class__.__name__ == 'ManyRelatedManager':
                    related_instances = [cgi.escape(repr(related_instance)) \
                                            for related_instance in val.all()]
                    val = "<br/>".join(related_instances)
                else:
                    val = cgi.escape(repr(val))
                printed_instance.append(val)
            printed_objects.append("".join(map(wrap_sth('td'),
                                               printed_instance)))

        # model name
        printed_model_name = wrap_sth('h3')(cgi.escape(unicode(model)))
        # model header
        printed_fields = "".join(map(wrap_sth('th'),
                                     map(cgi.escape, field_set)))
        printed_fields = wrap_sth('tr')(printed_fields)
        printed_fields = wrap_sth('thead')(printed_fields)
        # model instance
        printed_instances = "".join(map(wrap_sth('tr'),
                                        printed_objects))
        printed_instances = wrap_sth('tbody')(printed_instances)
        # table
        printed_table = "".join([
                            printed_model_name,
                            printed_fields, 
                            printed_instances])
        printed_table = wrap_sth('table')(printed_table)
        printed_models.append(printed_table)
    return render(request,
                  'test/test_page.html',
                  {'table': mark_safe("".join(printed_models))})
        
            
            

