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


# -------------
# main
# -------------
DEFAULT_PORT = 9527


def server(opts):
    if isinstance(opts.port, int):
        port = opts.port
    else:
        port = DEFAULT_PORT

    if opts.dir:
        os.chdir(opts.dir)

    simplehttp(port)


def simplehttp(port):
    httpd = SocketServer.TCPServer(('', port), PeonServerHandler, False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()

    print '------------'
    print 'Peon server'
    print 'Start SimpleHTTPServer at http://localhost:' + str(port) + '/'
    print 'Press Ctl+C to stop the server'
    print '------------'

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        httpd.shutdown()


if __name__ == '__main__':
    import argparse
    # command line options
    parser = argparse.ArgumentParser(
        description='Options of run Peon dev server.')

    parser.add_argument('-s', '--server',
                        dest='port',
                        action='store',
                        nargs='?',
                        type=int,
                        const=9527,
                        help='Start Peon dev server at port.')

    parser.add_argument('--dir',
                        dest='dir',
                        action='store',
                        nargs='?',
                        type=str,
                        const=None,
                        help='Define operation dir.')

    opts, unknown = parser.parse_known_args()

    server(opts)
