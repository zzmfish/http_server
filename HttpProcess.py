import os
import multiprocessing
import SocketServer
import signal
import socket
import urlparse
import time
from SimpleHTTPServer import SimpleHTTPRequestHandler

http_process = None

def log(msg):
  #open('/home/zhouzm/HttpProcess.log', 'a+').write(msg + '\n')
  print msg

http_process = None

def term_handler(signum, frame):
  global http_process
  http_process.stopped = True

class RequestHandler(SimpleHTTPRequestHandler):
    def parse_query(self):
        query = {}
        path = self.path
        p = path.find('?')
        if p >= 0:
            query = urlparse.parse_qs(path[p+1:])
        return query

    def handle_slow(self, query):
        t = float(query['__slow'][0])
        f = self.send_head()
        if f:
            content = f.read()
            p = len(content) / 2
            self.wfile.write(content[0 : p])
            time.sleep(t)
            self.wfile.write(content[p : ])
            f.close()
        
    def do_GET(self):
        query = self.parse_query()
        if query.has_key('__slow'):
            return self.handle_slow(query)
            
        return SimpleHTTPRequestHandler.do_GET(self)

class HttpProcess(multiprocessing.Process):
  def __init__(self, root, host, port):
    log('HttpProcess.__init__(root=%s, host=%s, port=%d)' % (root, host, port))
    global http_process
    multiprocessing.Process.__init__(self)
    self.root = root
    self.host = host
    self.port = port
    self.stopped = False
    http_process = self
    signal.signal(signal.SIGTERM, term_handler)

  def run(self):
    log('HttpProcess.run')
    os.chdir(self.root)
    Handler = RequestHandler
    httpd = SocketServer.TCPServer((self.host, self.port), Handler, False)
    httpd.timeout = 1
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    while not self.stopped:
      httpd.handle_request()
    httpd.socket.shutdown(socket.SHUT_RDWR)
    httpd.socket.close()

