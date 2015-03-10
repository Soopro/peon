#coding=utf-8
from __future__ import absolute_import
import argparse, os, sys, traceback
import SimpleHTTPServer, SocketServer
import coffeescript, lesscpy, pyjade
from StringIO import StringIO


class PeonServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    REWRITE_ROOT = "index"
    REWRITE_EXT = "html"
    
    PARSE_FILE_LIST = {
        'js':{'parse':'coffee', 'content_type':'text/javascript'},
        'html':{'parse':'jade', 'content_type':'text/html'},
        'css':{'parse':'less', 'content_type':'text/css'},
    }
    DEFAULT_PARSE_FILE = {'parse':None, 'content_type':'text/plain'}
    
    def do_GET(self):
        print "==========================================="
        print "Client requested:", self.command, self.path

        file_path, render_type = self.path_parse(self.path)
        self.render(file_path, render_type)
        return


    def path_parse(self, path):
        cwd = os.getcwd()
        path = os.path.join(cwd, path.lstrip('/'))

        file_path = None
        render_type = None

        filename, ext = os.path.splitext(path)

        if filename[-1:] is "/":
            filename = os.path.join(filename, self.REWRITE_ROOT)

        ext = ext[1:]
        if not ext:
            ext = self.REWRITE_EXT

        return filename, ext


    def render(self, filename, filetype):
        file_path = "{}.{}".format(filename, filetype)
        if filetype in self.PARSE_FILE_LIST:
            file_parse = self.PARSE_FILE_LIST[filetype]
        else:
            file_parse = self.DEFAULT_PARSE_FILE

        if not os.path.isfile(file_path):
            filetype = file_parse['parse']
            file_path = "{}.{}".format(filename, filetype)
        
        if not os.path.isfile(file_path):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            return
        
        with open(file_path, 'r') as f:
            file = f.read().strip('\n')
        f.closed
        
            
        resp_code = 200
        content = None
        content_type = file_parse['content_type']
        
        render_type = filetype
        
        if render_type == 'coffee':
            try:
                content = coffeescript.compile(file)
            except Exception as e:
                content = self.errorhandler(e, "Coffeescript Compiler Error:")

        elif render_type == 'less':
            try:
                content = lesscpy.compile(StringIO(file), minify=False)
            except Exception as e:
                content = self.errorhandler(e, "Less Compiler Error:")

        
        elif render_type == 'jade':
            try:
                content = pyjade.ext.html.process_jade(file)
                print type(content)
            except Exception as e:
                content = self.errorhandler(e, "Jade Compiler Error:")
        else:
            content = file

        self.send_response(resp_code)
        self.send_header('Content-type', content_type+";charset=utf-8")
        self.end_headers()
        # Send the html message; wfile is a StringIO in super class.
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        self.wfile.write(content)

    def errorhandler(self, err, err_type):
        err_msg = "{}\n{}".format(err_type, repr(err))
        print '----------- ERROR! --------------'
        print err_msg
        print '---------------------------------'
        print traceback.format_exc()
        return err_msg


def command_options():
    # command line options
    parser = argparse.ArgumentParser(
                    description='Options of run Peon dev server.')

    parser.add_argument('-p', '--port', 
                        dest='server_port',
                        action='store',
                        type=int,
                        help='Setup port.')

    opts, unknown = parser.parse_known_args()
    return opts


DEFAULT_PORT = 9527

def server():
    opts = command_options()
    if opts.server_port:
        PORT = opts.server_port
    else:
        PORT = DEFAULT_PORT
    
    httpd = SocketServer.TCPServer(("", PORT), PeonServerHandler,False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()

    print "/*----------------------------"
    print "Peon serving at port:", PORT
    print "/*----------------------------"

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit) as e:
        httpd.shutdown()

if __name__ == "__main__":
    server()