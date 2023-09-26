#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    OKHeader = 'HTTP/1.1 200 OK\r\n'
    RedirectHeader = 'HTTP/1.1 301 Moved Permanently\r\n'
    NotFoundHeader = 'HTTP/1.1 404 Not Found\r\n\r\n'
    NotValidHeader = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        data_info = self.data.decode('utf-8').split() # this should be [header, path]

        # check if we have a valid header
        # for this assignment, we should only be accepting GET headers
        if (data_info[0] == "GET"):
            self.handleResponse(data_info[1])
        else:
            # send a 405
            self.invalidMethod()
            return
        

        # outside of a handle request
        # we'll need to handle for all different headers
        # so we'll need 404, 405, 301, and 200

    def invalidMethod(self):
        """
            Function handler for 405 error status code
        """
        self.request.sendall(bytearray(self.NotValidHeader,'utf-8'))
        return
    
    def invalidResource(self):
        """
            Function handler for 404 error status code
        """
        self.request.sendall(bytearray(self.NotFoundHeader,'utf-8'))
        
        
    def handleRedirect(self, path):
        """
            Function handler for 301 status code
        """
        self.request.sendall(bytearray(self.RedirectHeader +"Location:" + path +'/' +"\r\n",'utf-8'))
    
    def handleHtml(self, path):
        """
            Function handler for 200 status code for any html files being accessed
            Returns as an exception
        """
        try:
            file = open(path, "r")
            content = file.read()
            self.request.sendall(bytearray(self.OKHeader + "Content-Type: text/html\r\n" + content,'utf-8'))
            return
        except Exception as e:
            self.invalidResource()
            return e
    
    def handleCss(self, path):

        try:
            file = open(path, "r")
            content = file.read()
            self.request.sendall(bytearray(self.OKHeader + "Content-Type: text/css\r\n" + content,'utf-8'))
            return
        except Exception as e:
            self.invalidResource()
            return

    # Handles 404, 301, 200
    def handleResponse(self, path):
        """
            Called when we have a valid response 
            In this case, we are only accepting the GET header
        """

        # We want to first check the exact size of the overall query
        # if we are passed 2 args, then we have been requested a possible file to open
        # our logic will then need to look into our own ./www folder and render the files there
        # if we can't access their requested files, then we must do a redirect 301

        if ".css" not in path and ".html" not in path: # check if it is a directory 
            if path[-1] == "/": # for the requirement of path ending
                path += "index.html"
            else: 
                # results in a 301 status code
                self.handleRedirect(path)
                return
                
        resource_directory = "./www" + path

        if (resource_directory.endswith('.html')):
            self.handleHtml(resource_directory)
        elif (resource_directory.endswith('.css')):
            self.handleCss(resource_directory)
        else:
            self.invalidResource()
            return

        return
        '''
        # Non working garbage
        try:
            # within our try clause we'll look to access the file
            if ( len(path.split(".")) > 1):
                if (path.endswith('.html')):
                    self.handleHtml(path)
                elif (path.endswith('.css')):
                    self.handleCss(path)
                else:
                    self.invalidResource()

            else:
                if (path[-1] == '/'):
                    path += 'index.html'
                    self.redirectRequest(path)
                else:
                    self.invalidResource()
            return
        
        except Exception as e:
            self.invalidResource()
            return
        '''        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
