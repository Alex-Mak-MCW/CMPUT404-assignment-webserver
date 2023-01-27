#  coding: utf-8 
import socketserver
import os
import os.path

# Copyright 2023 Abram Hindle, Eddie Antonio Santos, Alex Mak
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
    # User-defined method to get the file content and return it
    def getFileContent(self, file):
        fin=open(file)
        content=fin.read()
        fin.close()
        return content

    # User-defined method to send 200 responses based on content type(ext)
    # Learned the format of the HTTP 200 response status code from the source below

    # Source Title: 200 OK
    # Source Type: Website
    # Source author: MDN contributors (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200/contributors.txt)
    # Source License: CC BY-SA 2.5
    # Latest date contributed: November 26th, 2022
    # URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200
    def send200(self, content, ext):
        newbytearray='HTTP/1.1 200 OK\r\nContent-Type:text/'+ext+'\r\n\r\n'+content
        self.request.sendall(bytearray(newbytearray, "utf-8"))

    # User-defined method to handle all the cases that leads to 404 and send the 404 response
    # Learned the format of the HTTP 404 response status code from the source below

    
    # Source Title: 404 Not Found
    # Source Type: Website
    # Source author: MDN contributors (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404/contributors.txt)
    # Source License: CC BY-SA 2.5
    # Latest date contributed: November 26th, 2022
    # URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
    def send404(self):
        newbytearray="HTTP/1.1 404 Not Found\r\nPath Not Found\r\n"
        self.request.sendall(bytearray(newbytearray, "utf-8"))

    # Main method for the server to handle the requests
    def handle(self):
        # receiving data (already in b'')
        self.data = self.request.recv(1024).strip()

        # Convert data from bytes array to string, learned from the source below

        # Source Title: Convert bytes to a string
        # Source Type: Website (StackOverflow)
        # Source contributor: Aaron Maenppa(author, URL: https://stackoverflow.com/users/2603/aaron-maenpaa) and Mateen Ulhaq (editor, URL: https://stackoverflow.com/users/365102/mateen-ulhaq)
        # Source License: CC BY-SA 4.0
        # Latest date contributed: June 6th, 2022
        # Resource URI: https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        str_data=self.data.decode("utf-8")

        # Get each line percisely using list object to split lines
        list_data=str_data.split("\r\n")

        # 0:HTTP request; 1: accept encoding; 2: Host number; 3: User-agent; 4: connection 
        HTTP_header=list_data[0]
        request_method=HTTP_header.split()[0]
        path=HTTP_header.split()[1]
        full_path="./www"+path

        # Temporary byte array used to send http responses in the future
        newbytearray=''

        # Basic check: Empty data
        # if the decoded data is empty (just incase) -> send 400 Bad Request response
        # Learned the format of the HTTP 400 response status code from the source below

        # Source Title: 400 Bad Request
        # Source Type: Website
        # Source author: MDN contributors (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400/contributors.txt)
        # Source License: CC BY-SA 2.5
        # Latest date contributed: November 26th, 2022
        # URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
        if not str_data:
            newbytearray='HTTP/1.1 400 Bad Request\r\n\r\n'
            self.request.sendall(bytearray(newbytearray, "utf-8"))

        # if decoded data NOT EMPTY
        else:
            # Testing 405
            restricted_methods=['POST','PUT','DELETE']
            # if the request type belong to one of the 3 methods we cannot handle (POST, PUT, DELETE), then send 405 request
            # Learned the format of the HTTP 405 response status code from the source below

            # Source Title: 405 Method Not Allowed
            # Source Type: Website
            # Source author: MDN contributors (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405/contributors.txt)
            # Source License: CC BY-SA 2.5
            # Latest date contributed: November 26th, 2022
            # URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405
            if request_method in restricted_methods:
                newbytearray='HTTP/1.1 405 Method Not Allowed\r\n\r\n'
                self.request.sendall(bytearray(newbytearray, "utf-8"))

            # Path part to check directories and files, first check whether path exists
            elif os.path.exists(full_path):
                # extra test to handle the test from not-free-tests.py/ path attempt to leave current directory, send 404 if happened
                if ".." in full_path:
                    self.send404()

                # handling directory, check whether file is in a directory
                # Learned how to do so using the os and os.path modules and the method os.path.isdir from the source below

                # Source Title: Python: Check if a File or Directory Exists
                # Source Type: Website
                # Source author: Nikhil Aggarwal
                # Source License: CC BY-SA 
                # Latest date contributed: October 21st, 2022
                # URL: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
                elif os.path.isdir(full_path):
                    # Check if it is just a directory by checking whether path end with "/", 
                    # if it is, then add "index.html" on the path, read its content and send 200/ 404 depends index.html is empty or not
                    if path[-1]=='/':
                        temp=full_path+"index.html"
                        content=self.getFileContent(temp)

                        # If the file (.../index.html) is not empty-> 200 ok code
                        if content!= None:
                            self.send200(content, "html")
                        # If the file is actually empty (nothing read)-> 404 
                        else:
                            self.send404()

                    # if directory existed but doesn't end with "/", then send 301 message with the redirected path
                    # Learned the format of the HTTP 301 response status code from the source below

                    # Source Title: 301 Moved Permanently
                    # Source Type: Website
                    # Source author: MDN contributors (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301/contributors.txt)
                    # Source License: CC BY-SA 2.5
                    # Latest date contributed: November 26th, 2022
                    # URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
                    else:
                        newbytearray="HTTP/1.1 301 Moved Permanently\r\nLocation: "+path+"/\r\n"
                        self.request.sendall(bytearray(newbytearray, "utf-8"))

                # File part: check whether the path has a file or not
                # Learned how to do so using the os and os.path modules and the method os.path.isfile from the source below

                # Source Title: How to Check if a File Exists in Python with isFile() and exists()
                # Source Type: Website
                # Source author: Dionysia Lemonaki
                # Source License: BSD-3
                # Latest date contributed: January 5th, 2023
                # URL: https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/ 
                elif os.path.isfile(full_path):
                    # if it is a file, get its content and send 200/404 code depends whether the file is empty or not
                    content=self.getFileContent(full_path)
                    
                    # If the file is not empty-> send 200 ok code
                    if content!= None:
                        # if the file is html type, then send 200 code with html content

                        # Learned from the source below to use the os.path.splittext() method to get parts of a path in order to obtain a path's file extension.
                        
                        # Source Title: How can I check the extension of a file?
                        # Source Type: Website (StackOverflow)
                        # Source author: Acorn (URL: https://stackoverflow.com/users/311220/acorn)
                        # Source License: CC BY-SA 3.0
                        # Latest date contributed: May 5th, 2011
                        # Resource URI: https://stackoverflow.com/questions/5899497/how-can-i-check-the-extension-of-a-file 
                        if os.path.splitext(full_path)[-1].lower()==".html":
                            self.send200(content, "html")

                        # if the file is css type, then send 200 code with css content
                        elif os.path.splitext(full_path)[-1].lower()==".css":
                            self.send200(content, "css")
                    # If the file is actually empty (nothing read)-> send 404 
                    else:
                        self.send404()
                # neither file or directory-> send 404
                else:
                    self.send404()
            # If the path doesn't exist at all-> send 404
            else:
                self.send404()

        # printing the request itself, uncomment whenever for future testing
        # print ("Got a request of: %s\n" % str(self.data, 'utf-8'))
        # self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
