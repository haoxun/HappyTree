from __future__ import unicode_literals
# Create your views here.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.models import User, Group
from user_status.models import UserInfo
from group_info.models import GroupInfo

from file_info.utils import get_display_message_list
import operator


@login_required
def show_root(request):
    # realted group
    group_list = request.user.groups.all()
    group_info_list = [group.groupinfo for group in group_list]
    
    # relate project
    project_info_list = []
    for group_info in group_info_list:
       project_info_list.extend(group_info.normal_in_project.all())
       project_info_list.extend(group_info.super_in_project.all())
    # make unique
    project_info_list = list(set(project_info_list))
    
    # extract message
    message_set = []
    for project_info in project_info_list:
        message_set.extend(project_info.message_set.filter(post_flag=True))
    message_set = sorted(message_set, 
                         key=operator.attrgetter('post_time'), 
                         reverse=True)
    
    display_message_list = get_display_message_list(message_set, request.user)

    print display_message_list
    # rendering
    render_data_dict = {
            'user': request.user,
            'message_list': display_message_list,
    }
    return render(request, 
                  'user_status/root.html', 
                  render_data_dict)

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
    from project_info.models import ProjectInfo, Message
    from file_info.models import FileInfo, UniqueFile
    def wrap_sth(sth, foot=None):
        if foot == None:
            foot = sth
        def _wrap(target):
            return "<{0}>{1}</{2}>".format(sth, unicode(target), foot)
        return _wrap
    model_set = [User, Group, UserInfo, GroupInfo, ProjectInfo, Message, FileInfo, UniqueFile]
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
                    try:
                        val = getattr(instance, field + '_set')
                    except:
                        val = None
                # deal with many-to-many, many-to-one situation
                if val.__class__.__name__ in ['ManyRelatedManager', 'RelatedManager']:
                    related_instances = [cgi.escape(unicode(related_instance)) \
                                            for related_instance in val.all()]
                    val = "<br/>".join(related_instances)
                else:
                    val = cgi.escape(unicode(val))
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
        
            
            

