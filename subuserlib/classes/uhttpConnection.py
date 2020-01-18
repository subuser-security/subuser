# -*- coding: utf-8 -*-
# Taken from: http://www.openpanel.com/2007/08/http-on-unix-sockets-with-python/

"""
This module allows us to communicate using http over standard unix sockets.
"""

#external imports
import socket
try:
  import httplib
except ImportError:
  import http.client
  httplib = http.client
#internal imports
#import ...


class UHTTPConnection(httplib.HTTPConnection):
  """
  Subclass of Python library HTTPConnection that uses a unix-domain socket.
  """
  def __init__(self, path):
    httplib.HTTPConnection.__init__(self, 'localhost')
    self.path = path

  def connect(self):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(self.path)
    self.sock = sock
