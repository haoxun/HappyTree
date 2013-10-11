from __future__ import unicode_literals

import hashlib

def gen_MD5_of_UploadedFile(file):
    m = hashlib.md5()
    while True:
        data = file.read()
        if not data:
            return m.hexdigest()
        m.update(data)
