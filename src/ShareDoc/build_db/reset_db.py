import os
command = \
"""
rm sqlite3_db
python manage.py syncdb
echo "execfile('build_db/basic.py')" | python manage.py shell
python manage.py runserver
"""
os.system(command)
