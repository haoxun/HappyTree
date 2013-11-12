from __future__ import unicode_literals
# django dependency
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_objects_for_user
# model
from guardian.models import User
from message.models import Message
from project.models import Project
from message.models import UniqueFile
from message.models import FilePointer
# form
from message.forms import ProjectChoiceForm
from message.forms import MessageInfoForm
# decorator
# util
# python library
import json
import hashlib


class MessageBasicHandler(object):

    def _load_message_handler(self, request, message):
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
        return render(request,
                      'message/message_widget.html',
                      render_data_dict)

    def _uploaded_file_list_handler(self, request, message):
        render_data_dict = {
            'request': request,
            'message': message
        }
        return render(request,
                      'message/uploaded_file_list.html',
                      render_data_dict)

    def _upload_file_handler(self, request, message):
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
            json_data = json.dumps({
                'url': reverse('delete_file_pointer_from_message',
                               kwargs=keywords)
            })
            return HttpResponse(json_data, content_type='application/json')
        else:
            return HttpResponse("NOT OK")

class PostMessageHandler(object):

    def _post_message_handler(self, request, message):
        """
        Handle two kinds of message:
        1. newly created message.
        2. posted message.
        It's safe to have the same operation with both kinds.
        """
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
            # should return ERROR msg. Will be implemented later.
            raise PermissionDenied


class AJAX_CreateMessageHandler(MessageBasicHandler):
    
    def __init__(self, *args, **kwargs):
        super(AJAX_CreateMessageHandler, self).__init__(*args, **kwargs)

        create_message_handler = [
            ('load_message', self._load_message_handler),
            ('uploaded_file', self._upload_file_handler),
            ('load_file_list', self._uploaded_file_list_handler),
        ]

        self._register_handler(create_message_handler)

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


class NOTAJAX_CreateMessageHandler(PostMessageHandler):
    
    def __init__(self, *args, **kwargs):
        super(NOTAJAX_CreateMessageHandler, self).__init__(*args, **kwargs)
        create_message_handler = [
            ('post_message_submit', self._post_message_handler),
        ]

        self._register_handler(create_message_handler)


class AJAX_ModifyMessageHandler(MessageBasicHandler):
    
    def __init__(self, *args, **kwargs):
        super(AJAX_ModifyMessageHandler, self).__init__(*args, **kwargs)

        create_message_handler = [
            ('load_message', self._load_message_handler),
            ('uploaded_file', self._upload_file_handler),
            ('load_file_list', self._uploaded_file_list_handler),
        ]

        self._register_handler(create_message_handler)

    def _get_message(self, request, message_id):
        message = get_object_or_404(Message, id=int(message_id))
        return message


class NOTAJAX_ModifyMessageHandler(PostMessageHandler):
    
    def __init__(self, *args, **kwargs):
        super(NOTAJAX_ModifyMessageHandler, self).__init__(*args, **kwargs)
        create_message_handler = [
            ('post_message_submit', self._post_message_handler),
        ]

        self._register_handler(create_message_handler)
    

def gen_MD5_of_UploadedFile(file):
    m = hashlib.md5()
    CUT_SIZE = 65536
    if file.size < CUT_SIZE:
        content = file.read(file.size)
        m.update(content)
    else:
        start = file.read(CUT_SIZE)
        file.seek(-CUT_SIZE, 2)
        end = file.read(CUT_SIZE)
        m.update(start + end)
    return m.hexdigest()
