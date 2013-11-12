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
from message.utils import NOTAJAX_CreateMessageHandler
from message.utils import AJAX_ModifyMessageHandler
from message.utils import NOTAJAX_ModifyMessageHandler
# python library
import json
from datetime import datetime
import os
import mimetypes
mimetypes.init()


class CreateMessage(AJAX_CreateMessageHandler,
                    NOTAJAX_CreateMessageHandler,
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

    def post(self, request):
        message = self._get_message(request)
        return self._handler(request, message)
   

class ModifyMessage(AJAX_ModifyMessageHandler,
                    NOTAJAX_ModifyMessageHandler,
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
