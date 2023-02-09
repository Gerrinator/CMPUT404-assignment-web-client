#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Gerard van Genderen
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import time
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        print("Connected to %s on port %d" % (host, port))
        return None

    def get_code(self, data):
        return int(data.split(' ')[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url[1].split(':')
        host = netloc[0]
        if len(netloc) == 1:
            port = 80
        else:
            port = int(netloc[1])
        path = parsed_url[2]
        if path == '':
            path = '/'

        request = "GET %s HTTP/1.1\r\n" \
                  "Host: %s\r\n" \
                  "Accept: */*\r\n" \
                  "Connection: Close\r\n" \
                  "\r\n" % (path, host)
        try:
            self.connect(host, port)
            self.sendall(request)

            data = self.recvall(self.socket)
            self.close()

            code = self.get_code(data)
            body = self.get_body(data)
        except socket.gaierror:
            code = 404
            body = None
        else:
            print(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url[1].split(':')
        host = netloc[0]
        if len(netloc) == 1:
            port = 80
        else:
            port = int(netloc[1])
        path = parsed_url[2]
        if path == '':
            path = '/'

        content = ""

        if args != None:
            keys = args.keys()

            i = 0
            for key in keys:
                i += 1
                content += "%s=%s" % (key, args[key])
                if i < len(keys):
                    content += "&"

        request = "POST %s HTTP/1.1\r\n" \
                  "Host: %s\r\n" \
                  "Accept: */*\r\n" \
                  "Content-Type: application/x-www-form-urlencoded\r\n" \
                  "Content-Length: %d\r\n" \
                  "\r\n" \
                  "%s\r\n" % (path, host, len(content.encode('utf-8')), content)

        try:
            self.connect(host, port)
            self.sendall(request)

            data = self.recvall(self.socket)
            self.close()

            code = self.get_code(data)
            body = self.get_body(data)
        except socket.gaierror:
            code = 404
            body = None
        else:
            print(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
