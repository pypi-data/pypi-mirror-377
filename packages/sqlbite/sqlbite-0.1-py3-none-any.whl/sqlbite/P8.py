#tcp_client.py
import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 12345))
client_socket.sendall("Hello from TCP Client!".encode())
reply = client_socket.recv(1024).decode()
print("Server says:", reply)
client_socket.close()


#tcp_server.py
import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 12345))
server_socket.listen(1)
print("TCP Server is waiting for connection")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")
data = conn.recv(1024).decode()
print("Client says:", data)
conn.sendall("Hello from TCP SeRver".encode())
conn.close()
server_socket.close()


#udp_client.py
import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 54321)
client_socket.sendto("Hello from UDP Client!".encode(), server_address)
data, addr = client_socket.recvfrom(1024)
print("Server says:", data.decode())
client_socket.close()


#udp_server.py
import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 54321))
print("UDP Server is waiting for messege")
data, addr = server_socket.recvfrom(1024)
print(f"Client {addr} says:", data.decode())
server_socket.sendto("Hello from UDP Server".encode(), addr)
server_socket.close()
