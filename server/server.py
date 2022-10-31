import socket
import os

from cryptoo.ecdh import scalar_mult, make_keypair

from cryptoo.aes import AESCipher

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

        client_key = connect.recv(BUFFER_SIZE).decode()
        s_key = scalar_mult(client_key, self.private_key)
        connect.send(self.public_key)

        session_key = s_key[0]
        cipher = AESCipher(session_key)

        while True:
            data = cipher.decrypt(connect.recv(BUFFER_SIZE))
            if not data:
                break
            print("Request from client: " + str(data))

            command, file = data.split()
            file_name = str(file)
            file_path = "files/" + file_name + ("" if file_name.endswith(".txt") else ".txt")

            if command == 'r' or command == 'ch':
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    connect.send(cipher.encrypt(f"{file_path}{SEPARATOR}{file_size}"))

                    with open(file_path, "r") as f:
                        line_read = f.read(BUFFER_SIZE)
                        if not line_read:
                            connect.send(cipher.encrypt('file is empty'))
                        else:
                            connect.send(cipher.encrypt(line_read))

                    if command == 'ch':
                        with open(file_path, "w") as f:
                            line_read = connect.recv(BUFFER_SIZE)
                            f.write(cipher.decrypt(line_read))

                else:
                    connect.send(cipher.encrypt('such file doesn\'t exist'))

            if command == 'cr':
                with open(file_path, "w") as f:
                    pass

                file_size = os.path.getsize(file_path)
                connect.send(cipher.encrypt(f"{file_path}{SEPARATOR}{file_size}"))

            if command == 'del':
                if os.path.exists(file_path):
                    os.remove(file_path)

                connect.send(cipher.encrypt(f"{None}{SEPARATOR}{0}"))

        connect.close()  # close the connection


if __name__ == '__main__':
    server = Server(PORT_NUMBER, 1)
    server.process()
