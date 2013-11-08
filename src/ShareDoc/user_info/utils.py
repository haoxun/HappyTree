from __future__ import unicode_literals
# django dependency
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
# model
from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup 
from real_group.models import UserInfo_RealGroup_AC
from project.models import UserInfo_Project_AC 
from project.models import RealGroup_Project_AC
from real_group.models import BasicAC
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
from guardian.shortcuts import get_objects_for_user
# python library
from django.template.loader import render_to_string

class BasicACProcessor(object):
    
    def __init__(self, request, ac_id, decision):
        self.decision = decision
        self.request = request
        self._judge_perm()

    def _assign_perm(self, user):
        assign_perm(
            self.perm,
            user,
            self.ac,
        )

    def _remove_perm(self, user):
        remove_perm(
            self.perm,
            user,
            self.ac,
        )

    def _judge_perm(self):
        if self.ac.action_status == BasicAC.STATUS_FINISH:
            raise PermissionDenied
        elif self.ac.action_status != BasicAC.STATUS_WAIT\
                and self.decision != 'FINISH':
            raise PermissionDenied

    def _finish_handler(self):
        # if it's the last user
        if len(get_users_with_perms(self.ac)) == 1:
            self.ac.action_status = BasicAC.STATUS_FINISH
            self.ac.save()
        self._remove_perm(self.request.user)

    def _accept_handler(self):
        self.ac.action_status = BasicAC.STATUS_ACCEPT
        self.ac.save()
        # notify all related user
        self._set_ac_process_perm()

    def _deny_handler(self):
        self.ac.action_status = BasicAC.STATUS_DENY
        self.ac.save()
        # notify all related user
        self._set_ac_process_perm()

    def _handler_factory(self):
        if self.decision == 'ACCEPT':
            return self._accept_handler
        elif self.decision == 'DENY':
            return self._deny_handler
        elif self.decision == 'FINISH':
            return self._finish_handler

    def handle(self):
        handler = self._handler_factory()
        handler()


class ProcessUserProjectAC(BasicACProcessor):

    def __init__(self, request, ac_id, decision):
        self.user_project_ac = get_object_or_404(
            UserInfo_Project_AC,
            id=int(ac_id)
        )
        self.perm = 'project.process_user_project_ac'

        super(ProcessUserProjectAC, self).__init__(request, ac_id, decision)

    def _set_ac_process_perm(self):
        project = self.ac.project
        # assign perm to project's manager
        for user in get_users_with_perms(project):
            if user.has_perm('project_management', project):
                self._assign_perm(user)
        # assign perm to related user
        self._assign_perm(self.ac.user_info.user)

    def _accept_handler(self):
        user_info = self.ac.user_info
        project = self.ac.project
        project_group = project.project_group

        # add user
        project_group.group.user_set.add(user_info.user)
        assign_perm('project_membership', user_info.user, project)
        # add default permission
        if project_group.download:
            assign_perm('project_download', user_info.user, project)
        if project_group.upload:
            assign_perm('project_upload', user_info.user, project)
        if project_group.delete:
            assign_perm('project_delete', user_info.user, project)

        super(ProcessUserProjectAC, self)._accept_handler()


    def _get_user_project_ac(self):
        return self.user_project_ac

    ac = property(_get_user_project_ac)


class ProcessUserRealGroupAC(BasicACProcessor):

    def __init__(self, request, ac_id, decision):
        self.user_real_group_ac = get_object_or_404(
            UserInfo_RealGroup_AC,
            id=int(ac_id)
        )
        self.perm = 'real_group.process_user_real_group_ac'

        super(ProcessUserRealGroupAC, self).__init__(request, ac_id, decision)

    def _set_ac_process_perm(self):
        real_group = self.ac.real_group
        # assign perm to real group's manager
        for user in get_users_with_perms(real_group):
            if user.has_perm('group_management', real_group):
                self._assign_perm(user)
        # assign perm to related user
        self._assign_perm(self.ac.user_info.user)

    def _accept_handler(self):
        real_group = self.ac.real_group
        user_info = self.ac.user_info

        real_group.group.user_set.add(user_info.user)
        assign_perm(
            'real_group_membership',
            user_info.user,
            real_group,
        )

        super(ProcessUserRealGroupAC, self)._accept_handler()

    def _get_user_real_group_ac(self):
        return self.user_real_group_ac

    ac = property(_get_user_real_group_ac)


class ProcessRealGroupProjectAC(BasicACProcessor):

    def __init__(self, request, ac_id, decision):
        self.real_group_project_ac = get_object_or_404(
            RealGroup_Project_AC,
            id=int(ac_id),
        )
        self.perm = 'project.process_real_group_project_ac'

        super(ProcessRealGroupProjectAC, self).__init__(
            request,
            ac_id,
            decision
        )

    def _set_ac_process_perm(self):
        real_group = self.ac.real_group
        project = self.ac.project
        # assign perm to real group's manager
        for user in get_users_with_perms(real_group):
            if user.has_perm('group_management', real_group):
                self._assign_perm(user)
        # assign perm to project's manager
        for user in get_users_with_perms(project):
            if user.has_perm('project_management', project):
                self._assign_perm(user)

    def _accept_handler(self):
        real_group = self.ac.real_group
        project = self.ac.project
        project_group = project.project_group

        for user in real_group.group.user_set.all():
            # add user to project
            project_group.group.user_set.add(user)
            assign_perm(
                'project_membership',
                user,
                project,
            )
            # set default permission
            if project_group.download:
                assign_perm('project_download', user, project)
            if project_group.upload:
                assign_perm('project_upload', user, project)
            if project_group.delete:
                assign_perm('project_delete', user, project)
        project.real_groups.add(real_group)

        super(ProcessRealGroupProjectAC, self)._accept_handler()

    def _get_real_group_projce_ac(self):
        return self.real_group_project_ac

    ac = property(_get_real_group_projce_ac)


class ApplyConfirmHandler(object):

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

    notification_tuple = property(_get_alive_AC)


class NotificationCenter(object):
    
    def __init__(self, user):
        self.user = user

    def _get_notification_tuple(self):
        ac_tuple = ApplyConfirmHandler(self.user).notification_tuple
        return ac_tuple

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

        notification_tuple = self._get_notification_tuple()
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
