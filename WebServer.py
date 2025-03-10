#!/usr/bin/env python3 

import socket
import threading
import sys

host = '127.0.0.1'

if len(sys.argv) > 2:
    print(f"Usage: WebServer.py <port> ")
    sys.exit()


port = int(sys.argv[1])

def main():
    s_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    s_socket.bind((host,port))
    s_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    while True:

        conn,addr = s_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def handle_client(conn,addr):    
    request = conn.recv(1024).decode()

    # split the content into list
    lines = request.split("\r\n")
    if lines:
        request_line = lines[0]
        method,path,version =request_line.split()
    if method == "GET":
        if path == "/":
            path = "/index.html"
        
        try:
            with open('.' + path, "rb") as file:
                content = file.read()
            response_line = 'HTTP/1.1 200 OK\r\n'
            content_type = 'text/html' if path.endswith('.html') else 'image/png'
            headers = f'Content-Type: {content_type}\r\nContent-Length: {len(content)}\r\nConnection: keep-alive\r\n\r\n'
            response = response_line + headers
            conn.sendall(response.encode() + content)

        except FileNotFoundError:
            response_line = 'HTTP/1.1 404 Not Found\r\n'
            headers = 'Content-Type: text/html\r\n\r\n'
            content = '<html><body><h1>404 Not Found</h1></body></html>'
            response = response_line + headers + content
            conn.sendall(response.encode())

    else:
        response_line = 'HTTP/1.1 405 Method Not Allowed\r\n'
        headers = 'Content-Type: text/html\r\n\r\n'
        content = '<html><body><h1>405 Method Not Allowed</h1></body></html>'
        response = response_line + headers + content
        conn.sendall(response.encode())

    conn.close()



if __name__ == "__main__":
    main()


        


    
