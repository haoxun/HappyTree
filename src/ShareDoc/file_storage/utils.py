from __future__ import unicode_literals
import hashlib


def gen_MD5_of_UploadedFile(file):
    m = hashlib.md5()
    CUT_SIZE = 65536
    if file.size != CUT_SIZE:
        content = file.read(file.size)
        m.update(content)
    else:
        start = file.read(CUT_SIZE)
        file.seek(-CUT_SIZE, 2)
        end = file.read(CUT_SIZE)
        m.update(start + end)
    return m.hexdigest()
