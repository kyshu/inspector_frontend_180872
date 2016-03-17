import socket
import json

from StringIO import StringIO
from httplib import HTTPResponse
import logger

def encode(str):
    alphabet = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    length = len(str)
    enc = ""
    for i in range(4):
        mod = length%16
        length = length/16
        enc = alphabet[mod] + enc
    return enc+str

class FakeSocket:
    def __init__(self, str):
        self._file = StringIO(str)
    def makefile(self, *arg, **kwargs):
        return self._file

class Connection:
    def __init__(self, log=logger.Logger(logger.Logger.ERROR), adb_path="/usr/bin/adb"):
        self._logger = log
        self._sock = None

    def reset(self):
        self._sock.close()
        self._sock = None

    def query_pages(self, serial, usock, callback):
        self._connect_to_adb_server()
        def query_pages_by_json():
            cmd = "/json"
            return self._send_get_http_request(cmd, callback)
        self._forward_to_local_abstract(serial, usock, query_pages_by_json)

    def query_devices(self, callback):
        self._connect_to_adb_server()
        self._sock.send(encode("host:devices"));
        return self._checkResultAndProcess(callback)

    def get_remote_process(self, serial, callback):
        self._connect_to_adb_server()
        cmd = "shell:ps "
        def f():
            return self._send_cmd_to_adbd(cmd, callback)
        return self._transport_cmd(serial, f)

    def get_remote_unix_socks(self, serial, callback):
        self._connect_to_adb_server()
        cmd = "shell:cat /proc/net/unix"
        def f():
            return self._send_cmd_to_adbd(cmd, callback)
        return self._transport_cmd(serial, f)

    def _send_json_to_query_pages(self):
        cmd = "/json"
        return self._send_get_http_request(cmd, receive_pages)

    def _forward_to_local_abstract(self, serial, usock, callback):
        cmd = "localabstract:"+usock
        def f():
            return self._send_cmd_to_adbd(cmd, callback, void=True)
        return self._transport_cmd(serial, f)

    def _send_get_http_request(self, cmd, callback):
        request = "GET " + cmd + " HTTP/1.1\r\n\r\n"
        self._sock.send(request)
        return self._onHttpReceiveData(callback)

    def _onHttpReceiveData(self, callback):
        msg = self._sock.recv(4096)
        response = HTTPResponse(FakeSocket(msg))
        response.begin()
        #log.v("header: " + response.getheader('Content-Type'))
        #log.v("content: " + response.read(4096))
        #while msg != "":
        #    log.v("onHttpReceiveData: " + msg)
        #    msg = sock.recv(4096)
        return callback(response.read(4096))

    def _connect_to_adb_server(self):
        if (self._sock != None):
            self._logger.v("already connected")
            return
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            self._logger.e("can't create socket: ", msg)
            self._sock = None
            return
    
        try:
            self._sock.connect(("localhost", 5037))
            self._logger.v("connected " + repr(self._sock))
        except socket.error as msg:
            self._logger.e("can't connect to adb: ", msg)
            self._sock.close();
            self._sock = None
        return

    def _transport_cmd(self, serial, callback):
        transport_cmd = "host:transport:"+serial
        self._sock.send(encode(transport_cmd))
        return self._checkResultAndProcess(callback, is_transport=True, is_void=True)

    def _send_cmd_to_adbd(self, cmd, process, void=False):
        self._sock.send(encode(cmd))
        return self._checkResultAndProcess(process, is_transport=True, is_void=void)

    def _checkResultAndProcess(self, callback, arg1=None, arg2=None, is_transport=False, is_void=True):
        """
        is_void: set to false in transport mode for last command
        """
        res = self._sock.recv(1000)
        self._logger.v("receiveData " + res + " by sock: " + repr(self._sock))
        if len(res) < len("OKAY") or res[:4] != "OKAY":
            self._logger.e("failed to receive reponse " + res)
            return False

        if res[:4] == "OKAY":
            if is_transport==False:
                resLen = res[4:8]
                data = res[8:]
            else:
                if is_void==True:
                    if arg1!=None and arg2!=None:
                        return callback(arg1, arg2)
                    elif arg1!=None:
                        return callback(arg1)
                    else:
                        return callback()
                else:
                    #pull the remaining respond
                    data = ""
                    msg = self._sock.recv(1000)
                    while msg != "":
                        data = data+msg
                        msg = self._sock.recv(1000)
                    data = data+msg

            if arg1!=None and arg2!=None:
                return callback(data, arg1, arg2)
            elif arg1!=None:
                return callback(data, arg1)
            else:
                return callback(data)

        self._logger.e("checkResultAndProcess: unexpected branch")
        return False
