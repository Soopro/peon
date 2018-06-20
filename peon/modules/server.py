# coding=utf-8
from __future__ import absolute_import

import os
import SimpleHTTPServer
import SocketServer


# handlers
class PeonServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    REWRITE_ROOT = 'index'
    REWRITE_EXT = 'html'

    CONTENT_TYPES = {
        'js': {'content_type': 'text/javascript'},
        'html': {'content_type': 'text/html'},
        'css': {'content_type': 'text/css'},
    }
    DEFAULT_CONTENT_TYPE = {'content_type': 'text/plain'}

    def do_GET(self):
        self.path = self.path_parse(self.path)
        self.render()
        return

    def path_parse(self, path):
        filename, ext = os.path.splitext(path)

        if filename.endswith(os.path.sep):
            filename = os.path.join(filename, self.REWRITE_ROOT)

        ext = ext[1:]
        if not ext:
            ext = self.REWRITE_EXT

        path = '{}.{}'.format(filename, ext)

        return path

    def render(self):
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        return


def simplehttp(host, port):
    httpd = SocketServer.TCPServer((host, port), PeonServerHandler, False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()

    print '------------'
    print 'Peon server'
    print 'Start SimpleHTTPServer at http://{}:{}/'.format(host, port)
    print 'Press Ctl+C to stop the server'
    print '------------'

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        httpd.shutdown()


# -------------
# main
# -------------
DEFAULT_HOST = '127.0.0.1'  # leave it blank equals '0.0.0.0'
DEFAULT_PORT = 9527


def server(host=None, port=None, dir=None):
    host = str(host or DEFAULT_HOST)
    port = int(port or DEFAULT_PORT)

    if dir:
        os.chdir(dir)

    simplehttp(host, port)
