import time
import json
import hashlib


class format_save():
    def __init__(self, postfix):
        self.postfix = postfix
        self.total_cnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())

    def format_save(self, method, uri, version, header, body):
        print("================ FIND NEW VUL (%s) ================" % self.postfix)

        pkg_content = method + ' ' + uri + ' ' + version + '\n'
        hj = json.loads(header)
        for head in hj:
            pkg_content += head + ': ' + hj[head] + '\n'
        pkg_content += '\n'
        if method == 'POST':
            pkg_content += body

        fn = self.conf['scanner_path'] + "logs/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(
        )) + '_' + str(self.total_cnt).zfill(4) + '_' + self.postfix + '.txt'
        with open(fn, 'w') as fp:
            fp.write(pkg_content)

        self.total_cnt += 1


class check_repeat_package():
    def __init__(self):
        self.reqhash = []

    def is_repeat_pkg(self, method, uri, body):
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
