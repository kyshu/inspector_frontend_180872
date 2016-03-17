#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

import time
import threading
import os
import SimpleHTTPServer
import SocketServer
import subprocess
from subprocess import call
from subprocess import Popen


from lib.gui import *
from lib import logger
from lib.connection import Connection
from lib.browser import Browser
import inspector

#class HTTPServiceThread(threading.Thread):
#    def __init__(self, app):
#        threading.Thread.__init__(self)
#        self._app = app
#
#    def run(self):
#        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
#        self._app.httpd = SocketServer.TCPServer(("", 8000), Handler)
#        print "starting HTTP server..."
#        self._app.httpd.serve_forever()

class Application:
    def __init__(self):
        self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self._window.connect("delete_event", self.destroy)
        self._vBox = gtk.VBox()
        self._window.add(self._vBox)

        self._serviceRow = ServiceRow()
        self._vBox.pack_start(self._serviceRow.container())
        self._deviceRow = DeviceRow()
        self._vBox.pack_start(self._deviceRow.container())
        self._deviceRow.setRefreshCb(self.query_device)

        def onRemoteBrowserChanged(browser):
            call([self._adb_path, "forward", "tcp:9001", "localabstract:"+browser.getUsock()])

        def onBeginInspect(page):
            if not page.can_inspected():
                print "not inspectable"
                return
            if self.httpd == None:
                #self._thread = HTTPServiceThread(self)
                #self._thread.start()
                os.chdir(self._serviceRow.getRootDir())
                self.httpd = Popen(["python", "-m", "SimpleHTTPServer"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                time.sleep(1)

            print "ready to open url"
            Popen(["google-chrome", "http://localhost:8000/front_end/inspector.html?ws=localhost:9001" + page.getDebugFrontendUrl()])

        self._pageRow = PageRow(onRemoteBrowserChanged, onBeginInspect)
        self._vBox.pack_start(self._pageRow.container())


        self._vBox.show()
        self._window.show()

        # data
        self.httpd = None
        #self._thread = None
        self._adb_path = "/usr/bin/adb"
        call(["killall", "python"])

    def main(self):
        gtk.main()

    def destroy(self, widget, data=None):
        if self.httpd != None:
            print "clean up HTTP server"
            self.httpd.kill()
            self.httpd = None
        gtk.main_quit()

    def query_device(self, data):
        conn = Connection()
        serial_num = conn.query_devices(inspector.receiveDevices)
        conn.reset()
        self._deviceRow.setDevice(serial_num)

        processes = conn.get_remote_process(serial_num, inspector.echoData)
        conn.reset()

        opend_unix_socks = conn.get_remote_unix_socks(serial_num, inspector.echoData)
        conn.reset()

        remote_browsers = inspector.parseSocksAndProc(processes, opend_unix_socks)

        for browser in remote_browsers:
            browser.query_pages(serial_num, conn)
            browser.dump(logger.Logger(logger.Logger.VERBOSE))
            conn.reset()

        self._pageRow.setPackages(remote_browsers)


if __name__ == "__main__":
    app = Application()
    app.main()
