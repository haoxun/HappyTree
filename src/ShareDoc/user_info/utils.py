from __future__ import unicode_literals
# auth dependency
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user


class AJAX_HomePageHandler(object):

    def __init__(self, *args, **kwargs):
        super(AJAX_HomePageHandler, self).__init__(*args, **kwargs)

        self._register_handler([
            ('load_message_list', self._message_list_handler),
        ])

    def _message_list_handler(self, request):
        project_set = get_objects_for_user(request.user,
                                           'project.project_membership')
        message_set = []
        for project in project_set:
            message_set.extend(project.messages.filter(post_flag=True))
        message_set = sorted(
            message_set,
            key=lambda x: x.post_time,
            reverse=True
        )

        return render(
            request,
            'message/message_list.html',
            {'message_set': message_set},
        )


class AJAX_UserPageHandler(object):

    def __init__(self, *args, **kwargs):
        super(AJAX_UserPageHandler, self).__init__(*args, **kwargs)

        self._register_handler([
            ('load_message_list', self._message_list_handler),
        ])

    def _message_list_handler(self, request, user_info):
        message_set = user_info.messages.filter(
            post_flag=True,
        ).order_by(
            '-post_time',
        )
        return render(
            request,
            'message/message_list.html',
            {'message_set': message_set},
        )
