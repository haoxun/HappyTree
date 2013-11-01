from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
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
from project.models import Message
from project.models import Project
from file_storage.models import UniqueFile
from file_storage.models import FilePointer
# form
from file_storage.forms import ProjectChoiceForm
from file_storage.forms import FileUploadForm
from file_storage.forms import MessageInfoForm
# decorator
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
# util
from django.template.loader import render_to_string
from file_storage.utils import gen_MD5_of_UploadedFile
# python library
from datetime import datetime
import os
import mimetypes
mimetypes.init()


class CreateMessagePage(View):
    """
    This class handle the process of creating message, including
    1. init a message.
    2. handle the basic info of the message.
    3. handle the uploading file.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateMessagePage, self).dispatch(*args, **kwargs)

    def _get_message(self, request, forbid_init=False):
         # extract current processing message
        message = get_objects_for_user(request.user,
                                       'project.message_processing')
        if message:
            message = message[0]
        else:
            if forbid_init:
                raise PermissionDenied
            # if no current processing message, init one.
            project_set = get_objects_for_user(request.user,
                                               'project.project_upload')
            if len(project_set) == 0:
                # after finish dev, should give some error message about that,
                # instead of raising PermissionDenied
                raise PermissionDenied
            message = Message.objects.create(project=project_set[0],
                                             owner=request.user.userinfo)
            assign_perm('message_processing', request.user, message)
        return message

    def _load_message_handler(self, request):
        message = self._get_message(request)
        project_set = get_objects_for_user(request.user,
                                           'project.project_upload')
        form_select_project = ProjectChoiceForm(project_set)
        form_post_message = MessageInfoForm()

        render_data_dict = {
            'request': request,
            'message': message,
            'form_select_project': form_select_project,
            'form_post_message': form_post_message,
        }
        return render(request,
                      'file_storage/create_message.html',
                      render_data_dict)

    def get(self, request):
        if 'load_message' in request.GET:
            return self._load_message_handler(request)
        else:
            # forbid direct access
            raise PermissionDenied

    def _handler_factory(self, request):
        if 'uploaded_file' in request.POST:
            return self._upload_file_handler
        elif 'load_file_list' in request.POST:
            return self._uploaded_file_list_handler
        elif 'post_message_submit' in request.POST:
            return self._post_message_handler


    def _post_message_handler(self, request, message):
        project_set = get_objects_for_user(request.user,
                                           'project.project_upload')
        form_select_project = ProjectChoiceForm(project_set, request.POST)
        form_post_message = MessageInfoForm(request.POST)
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
            return redirect('home_page')
        else:
            render_data_dict = {
                'request': request,
                'message': message,
                'form_select_project': form_select_project,
                'form_post_message': form_post_message,
            }
            return render(request,
                          'file_storage/create_message_page.html',
                          render_data_dict)

    def _uploaded_file_list_handler(self, request, message):
        render_data_dict = {
            'request': request,
            'message': message
        }
        return render(request,
                      'file_storage/uploaded_file_list.html',
                      render_data_dict)

    def _upload_file_handler(self, request, message):
        uploaded_file = request.FILES['uploaded_file']
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
            return HttpResponse("OK")
        else:
            return HttpResponse("NOT OK")

    def post(self, request):
        message = self._get_message(request, forbid_init=True)
        handler = self._handler_factory(request)
        return handler(request, message)


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
    return redirect('home_page')


@require_GET
@login_required
def delete_file_pointer_from_message(request, file_pointer_id):
    file_pointer = get_object_or_404(FilePointer, id=int(file_pointer_id))
    unique_file = file_pointer.unique_file
    message = file_pointer.message
    project = message.project
    if not request.user.has_perm('project_delete', project):
        raise PermissionDenied

    reverse_url = request.GET.get('next', None)
    if not reverse_url:
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


@permission_required_or_403('project.project_membership',
                            (Project, 'id', 'project_id'))
def project_message_page(request, project_id):
    project = get_object_or_404(Project, id=int(project_id))
    message_set = project.messages.filter(post_flag=True).order_by('-post_time')

    render_data_dict = {
        'project': project,
        'message_set': message_set,
    }

    return render(request,
                  'file_storage/project_message_page.html',
                  render_data_dict)
