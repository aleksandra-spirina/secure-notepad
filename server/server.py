import socket
import os

from crypto.ecdh import scalar_mult, make_keypair

from crypto.aes import encrypt, decrypt

BUFFER_SIZE = 1024
PORT_NUMBER = 9090
SEPARATOR = "|"


class Server:

    def __init__(self, port, n):
        self.port = port
        self.max_user_number = n
        self.private_key, self.public_key = make_keypair()

    def process(self):
        host = socket.gethostname()

        server_socket = socket.socket()  # create server socket
        server_socket.bind((host, self.port))  # bind host address and port together

        server_socket.listen(self.max_user_number)
        connect, address = server_socket.accept()

        print(f"[+] {address} is connected.")
        print(f'public key = {self.public_key}')

        client_key_x = int.from_bytes(connect.recv(BUFFER_SIZE), 'big')
        connect.send(self.public_key[0].to_bytes(32, 'big'))

        client_key_y = int.from_bytes(connect.recv(BUFFER_SIZE), 'big')
        client_key = (client_key_x, client_key_y)
        connect.send(self.public_key[1].to_bytes(32, 'big'))

        print(f'client key = {client_key}')

        s_key = scalar_mult(self.private_key, client_key)

        session_key = s_key[0]

        while True:
            data = decrypt(connect.recv(BUFFER_SIZE), session_key)
            if not data:
                break
            print("Request from client: " + str(data))

            command, file = data.split()
            file_name = str(file)
            file_path = "files/" + file_name + ("" if file_name.endswith(".txt") else ".txt")

            if command == 'r' or command == 'ch':
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    connect.send(encrypt(f"{file_path}{SEPARATOR}{file_size}", session_key))

                    with open(file_path, "r") as f:
                        line_read = f.read(BUFFER_SIZE)
                        if not line_read:
                            connect.send(encrypt('file is empty', session_key))
                        else:
                            connect.send(encrypt(line_read, session_key))

                    if command == 'ch':
                        with open(file_path, "w") as f:
                            line_read = connect.recv(BUFFER_SIZE)
                            f.write(decrypt(line_read, session_key))

                else:
                    connect.send(encrypt('such file doesn\'t exist', session_key))

            if command == 'cr':
                with open(file_path, "w") as f:
                    pass

                file_size = os.path.getsize(file_path)
                connect.send(encrypt(f"{file_path}{SEPARATOR}{file_size}", session_key))

            if command == 'del':
                if os.path.exists(file_path):
                    os.remove(file_path)

                connect.send(encrypt(f"{None}{SEPARATOR}{0}", session_key))

        connect.close()  # close the connection


if __name__ == '__main__':
    server = Server(PORT_NUMBER, 1)
    server.process()
