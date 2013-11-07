from guardian.models import User
from user_info.models import UserInfo

# create users
name_set = open('build_db/names').read().split(',')
for name in name_set:
    user = User.objects.create_user(
        username=name,
        password="111111"
    )
    user_info = UserInfo.objects.create(
        user=user,
        email="{}@fuckyou.com".format(name)
    )
