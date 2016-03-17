#!/usr/bin/python

import os
import platform
import socket
import json

from StringIO import StringIO
from httplib import HTTPResponse
from urlparse import urlparse

from lib import logger
from lib.connection import Connection
from lib.browser import Browser

adb_path = "/usr/bin/adb"

log = logger.Logger(logger.Logger.ERROR)

def receiveDevices(msg):
    devices = msg.split('\n');
    if len(devices) > 2:
        log.i("multiple devices connected, inspect to :" + devices[0])

    return devices[0][:devices[0].find('\t')]

def echoData(data):
    return data

def parseSocksAndProc(proc, usocks_str):
    remote_browsers = []
    pids = []
    usocks = []

    lines = usocks_str.split('\n')
    for line in lines:
        if line.find("_devtools_remote") == -1:
            continue
        words = line.split()
        if words[7].find("chrome") != -1:
            pids.append("is_chrome")
            usocks.append(words[7])
        else:
            pids.append(words[7][words[7].find("_devtools_remote")+17:])
            usocks.append(words[7])

    lines = proc.split('\n')
    lines = lines[1:]
    for line in lines:
        if line == '':
            break
        words = line.split();
        for i, pid in enumerate(pids):
            if (pid == "is_chrome" and words[8] == "com.android.chrome") or pid == words[1]:
                remote_browsers.append(Browser(words[1], words[8], usocks[i][1:], pid == "is_chrome"))

    return remote_browsers

if __name__ == '__main__':
    conn = Connection(log)
    serial_num = conn.query_devices(receiveDevices)
    log.v("serial: "+serial_num)
    conn.reset()

    processes = conn.get_remote_process(serial_num, echoData)
    conn.reset()

    opend_unix_socks = conn.get_remote_unix_socks(serial_num, echoData)
    conn.reset()

    remote_browsers = parseSocksAndProc(processes, opend_unix_socks)
    if len(remote_browsers) == 0:
        exit(0)
        log.i("no remote browsers detect")

    for browser in remote_browsers:
        browser.query_pages(serial_num, conn)
        browser.dump(log)
        conn.reset()

    #5 get inspective url
    inspective_url = remote_browsers[0].inspect(0)
    
    exit(0)
