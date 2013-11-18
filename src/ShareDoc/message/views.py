from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.utils.http import urlencode
from django.views.generic.base import View
from rest_framework.views import APIView
from rest_framework.response import Response
# auth dependency
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403
from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_users_with_perms
from guardian.shortcuts import get_objects_for_user
# model
from guardian.models import User
from guardian.models import Group
from message.models import Message
from project.models import Project
from message.models import UniqueFile
from message.models import FilePointer
# form
from message.forms import ProjectChoiceForm
from message.forms import MessageInfoForm
# decorator
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
# util
from django.template.loader import render_to_string
from common.utils import POSTHandler
from message.utils import AJAX_CreateMessageHandler
from message.utils import AJAX_ModifyMessageHandler
# python library
import json
from datetime import datetime
import os
import mimetypes
mimetypes.init()


class AJAX_MessageWidget(APIView):

    def _get_message_widget(self, request, message):
        project_set = get_objects_for_user(request.user,
                                           'project.project_upload')
        # set content for posted message, which is safe to newly
        # created message.
        form_select_project = ProjectChoiceForm(
            project_set, 
            initial={'project_id': message.project.id},
        )
        form_post_message = MessageInfoForm(initial={
            'title': message.title,
            'description': message.description,
        })

        render_data_dict = {
            'request': request,
            'message': message,
            'form_select_project': form_select_project,
            'form_post_message': form_post_message,
        }
        return render(
            request,
            'message/message_widget.html',
            render_data_dict,
        )

    def _get_message(self, request):
        # request method other than GET
        message_id = request.DATA.get('message_id', None)
        # GET method
        message_id = message_id or request.GET.get('message_id', None)
        if message_id is None:
            raise PermissionDenied
        return get_object_or_404(Message, id=int(message_id))

    def _init_message(self, request):
         # extract current processing message
        message = get_objects_for_user(
            request.user,
            'message.message_processing',
        )
        if message:
            message = message[0]
        else:
            # if no current processing message, init one.
            project_set = get_objects_for_user(
                request.user,
                'project.project_upload',
            )

            if len(project_set) == 0:
                # after finish dev, should give some error message about that,
                # instead of raising PermissionDenied
                raise PermissionDenied

            message = Message.objects.create(
                project=project_set[0],
                owner=request.user.userinfo
            )
            assign_perm('message_processing', request.user, message)
        return message

    def _post_message(self, request, message):
        """
        Handle two kinds of message:
        1. newly created message.
        2. posted message.
        It's safe to have the same operation with both kinds.
        """
        project_set = get_objects_for_user(request.user,
                                           'project.project_upload')
        print request.DATA
        form_select_project = ProjectChoiceForm(project_set, request.DATA)
        form_post_message = MessageInfoForm(request.DATA)
        if form_post_message.is_valid() and form_select_project.is_valid():
            # set message info
            message.title = form_post_message.cleaned_data['title']
            message.description = form_post_message.cleaned_data['description']
            # target project
            project_id = form_select_project.cleaned_data['project_id']
            message.project = get_object_or_404(Project, id=int(project_id))
            # set post
            message.post_flag = True
            message.save()
            remove_perm('message_processing', request.user, message)
            return Response('OK')
        else:
            # should return ERROR msg. Will be implemented later.
            raise PermissionDenied

    def _delete_message(self, request, message):
        # only the owner of message can delete message.
        if request.user.userinfo != message.owner:
            raise PermissionDenied
        # cancel file_pointer
        for file_pointer in message.file_pointers.all():
            unique_file = file_pointer.unique_file
            file_pointer.delete()
            # I don't know, might not necessary.
            if unique_file.file_pointers.count() == 0:
                unique_file.delete()
        # safe
        remove_perm('message_processing', request.user, message)
        message.delete()

    # get message widget
    def get(self, request):
        message = self._get_message(request)
        return self._get_message_widget(request, message)

    # create message widget
    def post(self, request):
        message = self._init_message(request)
        return Response(message.id)

    # post/modify message
    def put(self, request):
        message = self._get_message(request)
        return self._post_message(request, message)

    # delete message
    def delete(self, request):
        message = self._get_message(request)
        self._delete_message(request, message)
        return Response('OK')


class CreateMessage(AJAX_CreateMessageHandler,
                    POSTHandler):
    """
    This class handles the process of creating message, including
    1. init a message.
    2. handle the basic info of the message.
    3. handle the uploading file.
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateMessage, self).dispatch(request, *args, **kwargs)

    def _get_message(self, request):
         # extract current processing message
        message = get_objects_for_user(
            request.user,
            'message.message_processing',
        )
        if message:
            message = message[0]
        else:
            # if no current processing message, init one.
            project_set = get_objects_for_user(
                request.user,
                'project.project_upload',
            )

            if len(project_set) == 0:
                # after finish dev, should give some error message about that,
                # instead of raising PermissionDenied
                raise PermissionDenied

            message = Message.objects.create(
                project=project_set[0],
                owner=request.user.userinfo
            )
            assign_perm('message_processing', request.user, message)
        return message

    def post(self, request):
        message = self._get_message(request)
        return self._handler(request, message)
   

class ModifyMessage(AJAX_ModifyMessageHandler,
                    POSTHandler):
    """
    This class handles the process of modification in posted message.
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # manually check permission
        message_id = kwargs.get('message_id', None)
        if message_id is None:
            raise PermissionDenied
        message = get_object_or_404(Message, id=int(message_id))
        if request.user.userinfo.id != message.owner.id:
            raise PermissionDenied
        return super(ModifyMessage, self).dispatch(request, *args, **kwargs)

    def _get_message(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        return message

    def post(self, request, message_id):
        message = self._get_message(request, message_id)
        return self._handler(request, message)


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=int(message_id))
    if request.user.userinfo != message.owner:
        raise PermissionDenied
    for file_pointer in message.file_pointers.all():
        unique_file = file_pointer.unique_file
        file_pointer.delete()
        if unique_file.file_pointers.count() == 0:
            unique_file.delete()
    remove_perm('message_processing', request.user, message)
    message.delete()
    return HttpResponse('OK')


@require_GET
@login_required
def delete_file_pointer_from_message(request, file_pointer_id):
    file_pointer = get_object_or_404(FilePointer, id=int(file_pointer_id))
    unique_file = file_pointer.unique_file
    message = file_pointer.message
    project = message.project

    if message.owner.user.id == request.user.id:
        pass
    elif not request.user.has_perm('project_delete', project):
        raise PermissionDenied

    reverse_url = request.GET.get('next', None)
    if reverse_url is None:
        raise PermissionDenied

    # delete file pointer
    file_pointer.delete()
    # smart pointer
    if unique_file.file_pointers.count() == 0:
        unique_file.delete()
    return HttpResponse('OK')


@login_required
def download_file(request, file_pointer_id):
    file_pointer = get_object_or_404(FilePointer, id=int(file_pointer_id))
    project = file_pointer.message.project
    if not request.user.has_perm('project_download', project):
        raise PermissionDenied
    unique_file = file_pointer.unique_file
    file_wrapper = FileWrapper(unique_file.file)
    # get content type
    # http://blog.robotshell.org/2012/deal-with-http-header-encoding-for-file-download/
    file_name = file_pointer.name
    # ugly code
    encode_file_name = urlencode(((file_name, ''),)).rstrip('=')

    content_type = os.path.splitext(file_name)[-1]
    content_type = mimetypes.types_map.get(content_type,
                                           'application/octet-stream')
    response = HttpResponse(file_wrapper,
                            content_type=content_type)
    content_disposition = "attachment; filename={0}; filename*=utf-8''{0}"
    response['Content-Disposition'] = content_disposition.format(encode_file_name)
    response['Content-Length'] = unique_file.file.size
    return response
