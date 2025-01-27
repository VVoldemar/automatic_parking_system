from socket import socket

client = socket()

client.connect(('127.0.0.1', 8765))
client.send("Hello!!!".encode())
client.close()