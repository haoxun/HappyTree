import os
import sys

if len(sys.argv) == 2:
    script_name = sys.argv[1]

    command = \
    """
    echo "execfile('build_db/{}')" | python manage.py shell
    """.format(script_name)
    os.system(command)
