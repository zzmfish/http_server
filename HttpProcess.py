import os
import multiprocessing
import SimpleHTTPServer
import SocketServer
import signal
import socket

http_process = None

def log(msg):
  #open('/home/zhouzm/HttpProcess.log', 'a+').write(msg + '\n')
  print msg

http_process = None

def term_handler(signum, frame):
  global http_process
  http_process.stopped = True

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
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer((self.host, self.port), Handler, False)
    httpd.timeout = 1
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    while not self.stopped:
      httpd.handle_request()
    httpd.socket.shutdown(socket.SHUT_RDWR)
    httpd.socket.close()

