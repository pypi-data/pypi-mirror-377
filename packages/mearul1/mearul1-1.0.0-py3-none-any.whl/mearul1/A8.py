#TCP Server

import socket
s = socket.socket()
s.bind(('127.0.0.1', 12345))
s.listen(1)
print("TCP Server waiting...")
c, a = s.accept()
print("Connected:", a)
data = c.recv(1024).decode()
print("Client:", data)
c.send("Hello from Server".encode())
c.close()
s.close()


#TCP Client
import socket

c = socket.socket()
c.connect(('127.0.0.1', 12345))
c.send("Hello from Client".encode())
print("Server:", c.recv(1024).decode())
c.close()


#UDP Server
import socket

s = socket.socket(socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 54321))
print("UDP Server waiting...")
msg, addr = s.recvfrom(1024)
print("Client:", msg.decode())
s.sendto("Hello from UDP Server".encode(), addr)
s.close()


#UDP Client
import socket

c = socket.socket(socket.SOCK_DGRAM)
addr = ('127.0.0.1', 54321)
c.sendto("Hello from UDP Client".encode(), addr)
msg, _ = c.recvfrom(1024)
print("Server:", msg.decode())
c.close()
