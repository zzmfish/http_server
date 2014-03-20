#!/usr/bin/python
import os
import HttpProcess

http_process = HttpProcess.HttpProcess(os.getcwd(), '127.0.0.1', 8080)
http_process.start()
http_process.join()
