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
from message.utils import gen_MD5_of_UploadedFile
# python library
import json
from datetime import datetime
import os
import mimetypes
mimetypes.init()


class AJAX_MessageWidget(APIView):

    def _get_message(self, request):
        # request method other than GET
        message_id = request.DATA.get('message_id', None)
        # GET method
        message_id = message_id or request.GET.get('message_id', None)
        if message_id is None:
            raise PermissionDenied
        return get_object_or_404(Message, id=int(message_id))

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

    def _init_message(self, request):
         # extract current processing message
        message = request.user.userinfo.messages.filter(post_flag=False)
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


class AJAX_SingleFile(APIView):

    def _get_file_pointer(self, request):
        file_pointer_id = request.DATA.get('file_pointer_id', None)
        file_pointer_id = file_pointer_id\
            or request.GET.get('file_pointer_id', None)
        if file_pointer_id is None:
            raise PermissionDenied
        return get_object_or_404(FilePointer, id=int(file_pointer_id))

    def _upload_file(self, request, message):
        uploaded_file = request.FILES.get('uploaded_file', None)
        if uploaded_file:
            # get or calculate MD5
            # https://github.com/marcu87/hashme
            md5 = request.POST.get('md5', None)
            if md5 is None:
                md5 = gen_MD5_of_UploadedFile(uploaded_file)
            # get unique file
            unique_file = UniqueFile.objects.filter(md5=md5)
            if not unique_file:
                # create unique file
                unique_file = UniqueFile.objects.create(md5=md5)
                # save md5 as its filename
                unique_file.file.save(md5, uploaded_file)
            else:
                unique_file = unique_file[0]
            # gen file pointer
            file_pointer = FilePointer.objects.create(
                name=uploaded_file.name,
                unique_file=unique_file,
                message=message,
            )

            keywords = {'file_pointer_id': file_pointer.id}
            json_data = {
                'url': "{0}?{1}".format(
                    reverse('message_file', kwargs={'message_id': message.id}),
                    urlencode(keywords),
                )
            }
            return Response(json_data)
        else:
            return Response("NOT OK")

    def _download_file(self, request, file_pointer):
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

    def _delete_file(self, request, file_pointer):
        unique_file = file_pointer.unique_file
        message = file_pointer.message
        project = message.project
    
        if message.owner.user.id == request.user.id:
            pass
        elif not request.user.has_perm('project_delete', project):
            raise PermissionDenied
    
        # delete file pointer
        file_pointer.delete()
        # smart pointer, still I don't know...
        if unique_file.file_pointers.count() == 0:
            unique_file.delete()
        return HttpResponse('OK')

    # download file
    def get(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        file_pointer = self._get_file_pointer(request)
        return self._download_file(request, file_pointer)

    # upload file
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        return self._upload_file(request, message)

    # delete file
    def delete(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        file_pointer = self._get_file_pointer(request)
        return self._delete_file(request, file_pointer)


class AJAX_FileList(APIView):

    def _get_file_list(self, request, message):
        render_data_dict = {
            'request': request,
            'message': message
        }
        return render(
            request,
            'message/uploaded_file_list.html',
            render_data_dict,
        )

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        return self._get_file_list(request, message)
