from guardian.models import User
from guardian.models import Group
from user_info.models import UserInfo
from real_group.models import RealGroup
from guardian.shortcuts import assign_perm
from datetime import datetime
import random

real_group_set = RealGroup.objects.all()
user_set = User.objects.filter(id__gte=0)

for real_group in real_group_set:
    member_size = random.randint(5, 21)
    for i in range(member_size):
        user = random.choice(user_set)
        real_group.group.user_set.add(user)
        assign_perm('real_group_membership', user, real_group)
