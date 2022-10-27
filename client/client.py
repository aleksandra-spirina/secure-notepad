import socket
import os

BUFFER_SIZE = 4096
PORT_NUMBER = 9090
SEPARATOR = "|"


def open_file(file_name):
    file_path = file_name + "" if file_name.endswith(".txt") else ".txt"
    to_command_string = "vim" + " " + file_path
    os.system(to_command_string)


class Client:

    def __init__(self, port):
        self.port = port

    def process(self):
        host = socket.gethostname()

        client_socket = socket.socket()
        print(f"[+] Connecting to {host}:{self.port}")
        client_socket.connect((host, self.port))
        print("[+] Connected.")

        message = input(" -> ")  # take input

        while message.lower().strip() != 'exit':
            client_socket.send(message.encode())
            command, file = message.split()

            received = client_socket.recv(BUFFER_SIZE).decode()
            if received == 'such file not exist':
                print(received)
                message = input(" -> ")
                continue

            file_name, filesize = received.split(SEPARATOR)

            file_name = os.path.basename(file_name)

            if command == 'r' or command == 'ch':
                if command == 'r':
                    line_read = client_socket.recv(BUFFER_SIZE)
                    print(line_read.decode())

                if command == 'ch':
                    with open(file_name, "w") as f:
                        line_read = client_socket.recv(BUFFER_SIZE)
                        if line_read.decode() == 'file is empty':
                            print(line_read.decode())
                        else:
                            f.write(line_read.decode())
                    open_file(file_name)

                    with open(file_name, "r") as f:
                        line_read = f.read(BUFFER_SIZE)
                        client_socket.send(line_read.encode())
                    os.remove(file_name)

            if command == 'cr':
                # on the server side
                pass

            if command == 'del':
                # on the server side
                pass

            message = input(" -> ")  # again take input

        client_socket.close()  # close the connection


if __name__ == '__main__':
    client = Client(PORT_NUMBER)
    client.process()
