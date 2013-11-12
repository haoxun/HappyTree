from __future__ import unicode_literals

from debug_page.utils import gen_models_debug_info
from django.shortcuts import render

def models_page(request):
    from guardian.models import User, Group
    from user_info.models import UserInfo
    from real_group.models import RealGroup
    from project.models import Project, ProjectGroup
    from message.models import Message
    from message.models import FilePointer, UniqueFile
    from notification.models import UserInfo_Project_AC, UserInfo_RealGroup_AC, RealGroup_Project_AC
    model_set = [
        User,
        UserInfo,
        Group,
        RealGroup,
        Project,
        ProjectGroup,
        Message,
        FilePointer,
        UniqueFile,
        UserInfo_RealGroup_AC,
        UserInfo_Project_AC,
        RealGroup_Project_AC,
    ]
    printed_html = gen_models_debug_info(model_set)
    return render(request,
                  'debug_page/test_page.html',
                  {'table': printed_html})
