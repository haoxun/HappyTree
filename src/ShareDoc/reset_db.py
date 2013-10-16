import os
command = \
"""
rm sqlite3_db
python manage.py syncdb
echo "execfile('script_build_db/build_test_user.py')" | python manage.py shell
python manage.py runserver
"""
os.system(command)
