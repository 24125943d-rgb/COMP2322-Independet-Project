import socket
import os
import threading
import time

# 1. Create a lock for thread-safe file writing
log_lock = threading.Lock()
LOG_FILE = "server_log.txt"

def write_log(client_ip, requested_file, status_code):
    """Write request details to the log file safely."""
    access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log_entry = f"[{access_time}] IP: {client_ip} | File: {requested_file} | Status: {status_code}\n"
    
    with log_lock:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    
    print(f"[LOG] {log_entry.strip()}")

def parse_headers(request_lines):
    headers = {}
    for line in request_lines[1:]:
        if line == '':
            break
        parts = line.split(': ', 1)
        if len(parts) == 2:
            headers[parts[0]] = parts[1]
    return headers

def generate_http_date(timestamp):
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))

def handle_client(client_socket, client_address, web_root):
    client_ip = client_address[0]
    client_socket.settimeout(10.0)
    
    try:
        while True:
            try:
                request_data = client_socket.recv(4096).decode('utf-8')
                if not request_data:
                    break
            except socket.timeout:
                break

            request_lines = request_data.split('\r\n')
            first_line = request_lines[0].split(' ')
            
            # 400 Bad Request
            if len(first_line) != 3:
                response = "HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n"
                client_socket.sendall(response.encode('utf-8'))
                write_log(client_ip, "Unknown", "400 Bad Request")
                break

            method, filepath, protocol = first_line
            headers = parse_headers(request_lines)
            
            connection_header = headers.get('Connection', 'close').lower()
            keep_alive = (connection_header == 'keep-alive')

            if filepath == '/': 
                filepath = '/index.html'
            target_file = os.path.join(web_root, filepath.lstrip('/'))

            # 404 Not Found
            if not os.path.exists(target_file) or not os.path.isfile(target_file):
                body = "<html><body><h1>404 Not Found</h1></body></html>"
                header = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(body)}\r\nConnection: {connection_header}\r\n\r\n"
                client_socket.sendall((header + body).encode('utf-8'))
                write_log(client_ip, filepath, "404 Not Found")
                if not keep_alive: break
                continue

            # 403 Forbidden
            if not os.access(target_file, os.R_OK):
                body = "<html><body><h1>403 Forbidden</h1></body></html>"
                header = f"HTTP/1.1 403 Forbidden\r\nContent-Length: {len(body)}\r\nConnection: {connection_header}\r\n\r\n"
                client_socket.sendall((header + body).encode('utf-8'))
                write_log(client_ip, filepath, "403 Forbidden")
                if not keep_alive: break
                continue

            mtime = os.path.getmtime(target_file)
            last_modified_str = generate_http_date(mtime)

            # 304 Not Modified
            if_modified_since = headers.get('If-Modified-Since')
            if if_modified_since and if_modified_since == last_modified_str:
                header = f"HTTP/1.1 304 Not Modified\r\nLast-Modified: {last_modified_str}\r\nConnection: {connection_header}\r\n\r\n"
                client_socket.sendall(header.encode('utf-8'))
                write_log(client_ip, filepath, "304 Not Modified")
                if not keep_alive: break
                continue

            # 200 OK
            with open(target_file, 'rb') as f:
                content = f.read()
            
            header = f"HTTP/1.1 200 OK\r\n"
            header += f"Content-Length: {len(content)}\r\n"
            header += f"Last-Modified: {last_modified_str}\r\n"
            header += f"Connection: {connection_header}\r\n\r\n"
            
            if method == 'GET':
                client_socket.sendall(header.encode('utf-8') + content)
            elif method == 'HEAD':
                client_socket.sendall(header.encode('utf-8'))
            
            write_log(client_ip, filepath, "200 OK")
            
            if not keep_alive:
                break

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        client_socket.close()

def start_server():
    HOST = '127.0.0.1'
    PORT = 8080
    WEB_ROOT = './www'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Final Server running at http://{HOST}:{PORT}")
        print(f"[*] Access logs will be saved to '{LOG_FILE}'\n")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address, WEB_ROOT)
            )
            client_thread.daemon = True 
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        server_socket.close()

if __name__ == '__main__':
    if not os.path.exists('./www'):
        os.makedirs('./www')
    start_server()