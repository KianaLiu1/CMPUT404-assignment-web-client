#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Copyright [2022] [Yuetong(Kiana) Liu]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ast import parse
import sys
import socket
import re
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
        return None

    def get_code(self, data):
        # https://www.w3schools.com/python/ref_string_split.asp
        parsedData = data.split("\r\n")
        return int(parsedData[0].split(" ")[1])

    def get_headers(self,data):
        parsedData = data.split("\r\n\r\n")
        headers = parsedData[0].split("\r\n")[1:] # All headers without the first line
        headerDict = {}
        for header in headers:
            temp = header.split(":")
            headerDict[temp[0]] = temp[1].strip()
        return headerDict

    def get_body(self, data):
        parsedData = data.split("\r\n\r\n")
        if len(parsedData) > 1:
            return parsedData[1]
        else:   # If no content provided
            return None
    
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
    def getParsedUrl(self, url):
        # https://docs.python.org/3/library/urllib.parse.html
        # https://stackoverflow.com/questions/7894384/python-get-url-path-sections
        path = urllib.parse.urlparse(url).path
        host = urllib.parse.urlparse(url).hostname
        port = urllib.parse.urlparse(url).port
        if port is None:
            port = 80
        if len(path) == 0:
            path = "/"
        return path, host, port

    def GET(self, url, args=None):
        path, hostName, port = self.getParsedUrl(url)
        # https://reqbin.com/req/nfilsyk5/get-request-example
        # Sending request
        self.connect(hostName, port)
        self.sendall("GET "+ path + " HTTP/1.1\r\nHost: "+hostName+"\r\nConnection: close\r\n\r\n")
        response = self.recvall(self.socket)
        print(self.get_body(response))
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)


        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # https://reqbin.com/code/python/ighnykth/python-requests-post-example
        path, hostName, port = self.getParsedUrl(url)

        request = "POST "+ path + " HTTP/1.1\r\nHost: "+hostName+"\r\nContent-Type: application/x-www-form-urlencoded\r\n"
        if args != None:
            # https://instructobit.com/tutorial/110/Python-3-urllib%3A-making-requests-with-GET-or-POST-parameters
            args = urllib.parse.urlencode(args)
            request += "Content-Length: "+ str(len(args))+"\r\n\r\n" + args + "\r\n"
        else:
            request += "Content-Length: 0\r\n\r\n"
        
        self.connect(hostName, port)
        self.sendall(request)

        response = self.recvall(self.socket)
        print(self.get_body(response))
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)


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
