#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
# Taken from: http://www.openpanel.com/2007/08/http-on-unix-sockets-with-python/

#external imports
import socket,httplib
#internal imports
#import ...


class UHTTPConnection(httplib.HTTPConnection):
    """Subclass of Python library HTTPConnection that uses a unix-domain socket.
    """
 
    def __init__(self, path):
        httplib.HTTPConnection.__init__(self, 'localhost')
        self.path = path
 
    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self.sock = sock

