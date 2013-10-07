
import os
import subprocess
os.putenv("PS1",  "dev:\W \u\$ ")
p = subprocess.Popen('/bin/bash --rcfile /Users/haoxun/Data/Project/Python/VIRTUALENV/Django/Active.sh'.split())
p.wait()
