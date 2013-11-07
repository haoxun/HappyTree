from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup
from guardian.shortcuts import assign_perm
from datetime import datetime
import random

user_set = User.objects.filter(id__gte=0)
group_size = len(user_set) / 10
for i in range(group_size):
    # random pick a user
    user = random.choice(user_set)

    name = "test_group_" + str(i)
    description = "test_description_" + str(i)
    unique_name = (
        '[real]',
        user.username,
        unicode(datetime.now()),
    )
    unique_name = "".join(unique_name)
    group = Group.objects.create(name=unique_name)
    # create related group info to handle group information
    real_group = RealGroup.objects.create(name=name,
                                          description=description,
                                          group=group)
    # set group's management permission to user
    assign_perm('real_group_ownership', user, real_group)
    assign_perm('real_group_management', user, real_group)
    assign_perm('real_group_membership', user, real_group)
    # relate user to group
    group.user_set.add(user)
