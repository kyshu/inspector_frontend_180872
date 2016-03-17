#!/usr/bin/python

class Logger:
    VERBOSE = 0
    ERROR = 1

    def __init__(self, level):
        self._level = level

    def v(self, msg):
        if self._level<=self.VERBOSE:
            print msg

    def e(self, msg):
        print "error:", msg

    def i(self, msg):
        print msg
