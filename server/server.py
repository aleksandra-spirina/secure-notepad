import socket
import os

BUFFER_SIZE = 1024
PORT_NUMBER = 9090
SEPARATOR = "|"


class Server:

    def __init__(self, port, n):
        self.port = port
        self.max_user_number = n

    def process(self):
        host = socket.gethostname()

        server_socket = socket.socket()  # create server socket
        server_socket.bind((host, self.port))  # bind host address and port together

        server_socket.listen(self.max_user_number)
        connect, address = server_socket.accept()

        print(f"[+] {address} is connected.")

        while True:
            data = connect.recv(BUFFER_SIZE).decode()
            if not data:
                break
            print("Request from client: " + str(data))

            command, file = data.split()
            file_name = str(file)
            file_path = "files/" + file_name + ("" if file_name.endswith(".txt") else ".txt")

            if command == 'r' or command == 'ch':
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    connect.send(f"{file_path}{SEPARATOR}{file_size}".encode())

                    with open(file_path, "r") as f:
                        line_read = f.read(BUFFER_SIZE)
                        if not line_read:
                            connect.send('file is empty'.encode())
                        else:
                            connect.send(line_read.encode())

                    if command == 'ch':
                        with open(file_path, "w") as f:
                            line_read = connect.recv(BUFFER_SIZE)
                            f.write(line_read.decode())

                else:
                    connect.send('such file not exist'.encode())

            if command == 'cr':
                with open(file_path, "w") as f:
                    pass

                file_size = os.path.getsize(file_path)
                connect.send(f"{file_path}{SEPARATOR}{file_size}".encode())

            if command == 'del':
                if os.path.exists(file_path):
                    os.remove(file_path)

                connect.send(f"{None}{SEPARATOR}{0}".encode())

        connect.close()  # close the connection


if __name__ == '__main__':
    server = Server(PORT_NUMBER, 1)
    server.process()
