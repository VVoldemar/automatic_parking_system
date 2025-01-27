from socket import socket, AF_INET
from threading import Thread


class SocketServer:
    server: socket
    therad: Thread

    def __init__(self):
        self.server = socket(AF_INET)
        self.therad = Thread(target=self.serve, daemon=False)
        self.therad.start()
    
    def serve(self):
        try:
            self.server.bind(('0.0.0.0', 8765))
            self.server.listen(1)

            while True:
                client, addr = self.server.accept()
                Thread(target=self.process_client, args=[client, addr], daemon=False).start()
        finally:
            self.server.close()
            print("Closed server")
    
    def process_client(self, client: socket, addr):
        while True:
            data = client.recv(2048)
            if data == None or len(data) == 0:
                break
            print(addr[0], data.decode())
        client.close()
        print("Closed: ", addr[0])


if __name__ == "__main__":
    server = SocketServer()
    server.therad.join()