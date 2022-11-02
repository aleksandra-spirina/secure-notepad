import socket
import os
from crypto.ecdh import make_keypair, scalar_mult
from crypto.serpent import encrypt, decrypt
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
        self.private_key, self.public_key = make_keypair()

    def process(self):
        host = socket.gethostname()

        client_socket = socket.socket()
        print(f"[+] Connecting to {host}:{self.port}")
        client_socket.connect((host, self.port))
        print("[+] Connected.")

        print(f'public key = {self.public_key}')

        client_socket.send(self.public_key[0].to_bytes(32, 'big'))
        server_key_x = int.from_bytes(client_socket.recv(BUFFER_SIZE), 'big')
        client_socket.send(self.public_key[1].to_bytes(32, 'big'))
        server_key_y = int.from_bytes(client_socket.recv(BUFFER_SIZE), 'big')
        server_key = (server_key_x, server_key_y)

        print(f'server key = {server_key}')

        s_key = scalar_mult(self.private_key, server_key)

        session_key = s_key[0]

        message = input(" -> ")  # take input

        while message.lower().strip() != 'exit':

            client_socket.send(encrypt(message, session_key))
            command, file = message.split()

            received = decrypt(client_socket.recv(BUFFER_SIZE), session_key)
            if received == 'such file not exist':
                print(received)
                message = input(" -> ")
                continue

            file_name, filesize = received.split(SEPARATOR)

            file_name = os.path.basename(file_name)

            if command == 'r' or command == 'ch':
                if command == 'r':
                    line_read = client_socket.recv(BUFFER_SIZE)
                    print(decrypt(line_read, session_key))

                if command == 'ch':
                    with open(file_name, "w") as f:
                        line_read = client_socket.recv(BUFFER_SIZE)
                        line_read_decrypted = decrypt(line_read, session_key)
                        if line_read_decrypted == 'file is empty':
                            print(line_read_decrypted)
                        else:
                            f.write(line_read_decrypted)
                    open_file(file_name)

                    with open(file_name, "r") as f:
                        line_read = f.read(BUFFER_SIZE)
                        client_socket.send(encrypt(line_read), session_key)
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
