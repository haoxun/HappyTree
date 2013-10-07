#!/usr/bin/python
# -*- coding: UTF-8 -*-
# generate two file, for auto active virtualenv environemet

import os
import sys

if len(sys.argv) != 2:
    raise Exception("Input ERROR!")
if target_dir not in os.listdir(cur_path):
    raise Exception("Dir Not Exist!")

cur_path = os.getcwd()
target_dir = sys.argv[1]
env_path = os.path.join(cur_path, target_dir)
active_shell_path = env_path + '/bin/activate'
active_file_path = os.path.join(env_path, 'Active.sh')

# write .sh to the root of env
command = \
"""
#!/bin/bash
. {}
"""
sh_file = open(active_file_path, 'w')
sh_file.write(command.format(active_shell_path))
sh_file.close()

# gen .py to run .sh
command = \
"""
import os
import subprocess
os.putenv("PS1",  "dev:\W \u\$ ")
p = subprocess.Popen('/bin/bash --rcfile {}'.split())
p.wait()
"""
active_file = open('{}_active.py'.format(target_dir), 'w')
active_file.write(command.format(active_file_path))
active_file.close()
