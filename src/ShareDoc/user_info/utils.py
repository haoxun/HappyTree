from __future__ import unicode_literals
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup 
from real_group.models import UserInfo_RealGroup_AC
from project.models import UserInfo_Project_AC 
from project.models import RealGroup_Project_AC
from guardian.shortcuts import get_objects_for_user

class ApplyConfirmDisplayFactory(object):
    def _get_alive_AC(self, user):

        def separate_user_project_ac(ac_list):
            UTP_ac = []
            PTU_ac = []
            for ac in ac_list:
                if ac.project in project_set:
                    UTP_ac.append(ac)
                else:
                    PTU_ac.append(ac)
            return UTP_ac, PTU_ac

        def separate_real_group_project_ac(ac_list):
            RTP_ac = []
            PTR_ac = []
            for ac in ac_list:
                if ac.project in project_set:
                    RTP_ac.append(ac)
                elif ac.real_group in real_group_set:
                    PTR_ac.append(ac)
            return RTP_ac, PTR_ac

        def separate_user_real_gorup_ac(ac_list):
            UTR_ac = []
            RTU_ac = []
            for ac in ac_list:
                if ac.real_group in real_group_set:
                    UTR_ac.append(ac)
                else:
                    RTU_ac.append(ac)
            return UTR_ac, RTU_ac

        def check_empty(ac_template_mapping, html_ac):
            empty = True
            for ac, template_name, tag_name in ac_template_mapping:
                if len(ac) != 0:
                    empty = False
                    break
            if empty:
                return render_to_string('user_info/non_ac.html')
            else:
                return html_ac

        # classify ACs
        user_project_ac = get_objects_for_user(
            user,
            'project.process_user_project_ac',
        )
        real_group_project_ac = get_objects_for_user(
            user,
            'project.process_real_group_project_ac',
        )
        user_real_group_ac = get_objects_for_user(
            user,
            'real_group.process_user_real_group_ac',
        )
        # Sth in which user can make decision
        real_group_set = get_objects_for_user(
            user,
            'real_group.real_group_management',
        )
        project_set = get_objects_for_user(
            user,
            'project.project_management',
        )

        UTP_ac, PTU_ac = separate_user_project_ac(user_project_ac)
        RTP_ac, PTR_ac = separate_real_group_project_ac(real_group_project_ac)
        UTR_ac, RTU_ac = separate_user_real_gorup_ac(user_real_group_ac)

        # decorate ACs according to its type, state



def gen_models_debug_info(model_set):
    import cgi
    from django.utils.safestring import mark_safe

    def wrap_sth(sth, foot=None):
        if foot is None:
            foot = sth

        def _wrap(target):
            return "<{0}>{1}</{2}>".format(sth, unicode(target), foot)
        return _wrap

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
                if val.__class__.__name__ in [
                        'ManyRelatedManager',
                        'RelatedManager']:
                    related_instances = []
                    for related_instance in val.all():
                        related_instances.append(
                            cgi.escape(unicode(related_instance))
                        )
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
            printed_instances
        ])
        printed_table = wrap_sth('table')(printed_table)
        printed_models.append(printed_table)

    return mark_safe("".join(printed_models))
