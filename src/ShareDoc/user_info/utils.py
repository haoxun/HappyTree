from __future__ import unicode_literals
# model
from guardian.shortcuts import get_objects_for_user
from django.template.loader import render_to_string

class NotificationCenter(object):
    
    def __init__(self, user):
        self.user = user

    def _get_alive_AC(self):

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
            self.user,
            'project.process_user_project_ac',
        )
        real_group_project_ac = get_objects_for_user(
            self.user,
            'project.process_real_group_project_ac',
        )
        user_real_group_ac = get_objects_for_user(
            self.user,
            'real_group.process_user_real_group_ac',
        )
        # Sth in which user can make decision
        real_group_set = get_objects_for_user(
            self.user,
            'real_group.real_group_management',
        )
        project_set = get_objects_for_user(
            self.user,
            'project.project_management',
        )

        UTP_ac, PTU_ac = separate_user_project_ac(user_project_ac)
        RTP_ac, PTR_ac = separate_real_group_project_ac(real_group_project_ac)
        UTR_ac, RTU_ac = separate_user_real_gorup_ac(user_real_group_ac)

        # decorate ACs according to its type, state
        ac_template_mapping = [
            (UTP_ac, 'user_info/single_UTP.html', 'ac'),
            (PTU_ac, 'user_info/single_PTU.html', 'ac'),
            (RTP_ac, 'user_info/single_RTP.html', 'ac'),
            (PTR_ac, 'user_info/single_PTR.html', 'ac'),
            (UTR_ac, 'user_info/single_UTR.html', 'ac'),
            (RTU_ac, 'user_info/single_RTU.html', 'ac'),
        ]
        notification_tuple = []
        for ac_set, template_name, tag_name in ac_template_mapping:
            for ac in ac_set:            
                html = render_to_string(template_name,
                                        {tag_name: ac})        
                created_time = ac.created_time
                notification_tuple.append(
                    (created_time, html),
                )

        return notification_tuple

    def _get_notification_html(self):
        
        def sort_tuple(notification_tuple):
            sorted_tuple =  sorted(
                notification_tuple,
                key=lambda x: x[0],
                reverse=True
            )
            return sorted_tuple

        def get_html(notification_tuple):
            return notification_tuple[1]

        notification_tuple = self._get_alive_AC()
        sorted_notification_tuple = sort_tuple(notification_tuple)

        return "".join(map(get_html, sorted_notification_tuple))

    notification_html = property(_get_notification_html)




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
