from __future__ import unicode_literals
# django dependency
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from guardian.shortcuts import assign_perm
from guardian.shortcuts import get_users_with_perms
# model
from user_info.models import UserInfo
from project.models import Project
from project.models import UserInfo_Project_AC
from project.models import RealGroup_Project_AC
from real_group.models import RealGroup
# form
# decorator
# util
# python library


def construct_user_project_ac(user_info_id, project_id, direction):
    if direction != 'ACTION_PTU' and direction != 'ACTION_UTP':
        raise PermissionDenied
    user_info = get_object_or_404(UserInfo, id=int(user_info_id))
    project = get_object_or_404(Project, id=int(project_id))
    if not UserInfo_Project_AC.objects.filter(
            user_info=user_info,
            project=project,
            action_code=getattr(UserInfo_Project_AC, direction),
            action_status=UserInfo_Project_AC.STATUS_WAIT):
        # ensure there's only one ac
        project_user_ac = UserInfo_Project_AC.objects.create(
            user_info=user_info,
            project=project,
            action_code=getattr(UserInfo_Project_AC, direction),
            action_status=UserInfo_Project_AC.STATUS_WAIT
        )
        if direction == 'ACTION_PTU':
            assign_perm(
                'project.process_user_project_ac',
                user_info.user,
                project_user_ac,
            )
        else:
            project_user_set = get_users_with_perms(project)
            for user in project_user_set:
                if user.has_perm('project_management', project):
                    assign_perm(
                        'project.process_user_project_ac',
                        user,
                        project_user_ac,
                    )


def construct_real_group_project_ac(real_group_id, project_id, direction):
    if direction != 'ACTION_PTR' and direction != 'ACTION_RTP':
        raise PermissionDenied
    real_group = get_object_or_404(RealGroup, id=int(real_group_id))
    project = get_object_or_404(Project, id=int(project_id))
    if not RealGroup_Project_AC.objects.filter(
            real_group=real_group,
            project=project,
            action_code=getattr(RealGroup_Project_AC, direction),
            action_status=RealGroup_Project_AC.STATUS_WAIT):
        # ensure there's only one ac
        real_group_project_ac = RealGroup_Project_AC.objects.create(
            real_group=real_group,
            project=project,
            action_code=getattr(RealGroup_Project_AC, direction),
            action_status=RealGroup_Project_AC.STATUS_WAIT,
        )
        if direction == 'ACTION_PTR':
            real_group_user_set = get_users_with_perms(real_group)
            for user in real_group_user_set:
                if user.has_perm('real_group_management', real_group):
                    assign_perm(
                        'project.process_real_group_project_ac',
                        user,
                        real_group_project_ac,
                    )
        elif direction == 'ACTION_RTP':
            project_user_set = get_users_with_perms(project)
            for user in project_user_set:
                if user.has_perm('project_management', project):
                    assign_perm(
                        'project.process_real_group_project_ac',
                        user,
                        real_group_project_ac,
                    )
