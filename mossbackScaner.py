# -*- coding: utf-8 -*-
# version: 0.2
# date: 2020.09.22

import json
import re
import socket
import sys
import http.client
import time
import threading

from socket import *
from time import ctime
import hashlib
import subprocess
from subprocess import PIPE
from scanner_sqli import test_sqli
from scanner_unauth_access import test_unauth_access
from color_print import *

global glo_conf
global glo_pkg_list
global glo_lock
global glo_scanner


def scanner_factory(name):
    return eval(name + "()")


with open('config.json', 'r') as fp:
    glo_conf = json.loads(fp.read())

glo_pkg_list = []

glo_lock = threading.Lock()

glo_scanner = []
glo_scanner.append(scanner_factory("test_sqli"))
glo_scanner.append(scanner_factory("test_unauth_access"))


def do_scan_thread():
    global glo_pkg_list
    global glo_lock
    global glo_scanner

    while True:
        glo_lock.acquire()
        if len(glo_pkg_list) > 0:
            pkg = json.loads(glo_pkg_list.pop(0))
            glo_lock.release()

            # do all test here
            for fun in glo_scanner:
                fun.run(pkg['method'], pkg['uri'], pkg['version'],
                        pkg['header'], pkg['body'], pkg['host'])
            # test finished
        else:
            glo_lock.release()
            time.sleep(1)


def main():
    global glo_pkg_list
    global glo_lock
    global glo_conf

    t = threading.Thread(target=do_scan_thread, args=())
    t.start()

    BUFSIZ = 1024
    ADDRESS = ('', glo_conf['scanner_port'])
    udpServerSocket = socket(AF_INET, SOCK_DGRAM)
    udpServerSocket.bind(ADDRESS)

    while True:
        # pack_meta = pack_cnt(4 B) + pack_hash(32 B)
        pack_meta, pack_from = udpServerSocket.recvfrom(36)
        pack_meta = pack_meta.decode()
        pack_data = ''
        for i in range(int(pack_meta[:4])):
            data, _ = udpServerSocket.recvfrom(BUFSIZ)
            pack_data += data.decode()

        m = hashlib.md5()
        m.update(pack_data.encode())

        if pack_meta[4:] != m.hexdigest():
            printDarkRed("[ERROR] the hash of received message incorrect.")
            udpServerSocket.sendto("ER".encode('utf-8'), pack_from)
        else:
            udpServerSocket.sendto("OK".encode('utf-8'), pack_from)

        glo_lock.acquire()
        glo_pkg_list.append(pack_data)
        glo_lock.release()

    udpServerSocket.close()


if __name__ == "__main__":
    main()
