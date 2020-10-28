import time
import json
import hashlib
import ctypes
import sys
from color_print import *


class format_save():
    def __init__(self, postfix):
        self.postfix = postfix
        self.total_cnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())

    def format_save(self, method, uri, version, header, body):
        printRed("================ FIND NEW VUL (%s) ================\nURI: %s %s" % (
            self.postfix, method, uri))

        pkg_content = method + ' ' + uri + ' ' + version + '\n'
        hj = json.loads(header)
        for head in hj:
            pkg_content += head + ': ' + hj[head] + '\n'
        pkg_content += '\n'
        if method == 'POST':
            pkg_content += body

        fn = self.conf['scanner_path'] + "logs/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(
        )) + '_' + str(self.total_cnt).zfill(4) + '_' + self.postfix + '.txt'
        with open(fn, 'w', errors='ignore') as fp:
            fp.write(pkg_content)

        self.total_cnt += 1


class check_repeat_package():
    def __init__(self, key_with_value=False):
        self.reqhash = []
        self.key_with_value = key_with_value

    def is_repeat_pkg(self, method, uri, body):
        if self.key_with_value is False:
            hash_msg = method
            uris = uri.split('?')
            hash_msg += uris[0]
            if len(uris) >= 2:
                parms = uris[1].split('&')
                for parm in parms:
                    hash_msg += parm.split('=')[0]
            if method == 'POST':
                parms = body.split('&')
                for parm in parms:
                    hash_msg += parm.split('=')[0]
            m = hashlib.md5()
            m.update(hash_msg.encode())
            h = m.hexdigest()
            if h in self.reqhash:
                return True

            self.reqhash.append(h)
            return False
        else:
            hash_msg = method + uri
            if method == 'POST':
                hash_msg += body
            m = hashlib.md5()
            m.update(hash_msg.encode())
            h = m.hexdigest()
            if h in self.reqhash:
                return True

            self.reqhash.append(h)
            return False
