import zpp_serpent


def encrypt(message, password):
    password = password.to_bytes(32, 'big')
    message_encrypted = (zpp_serpent.encrypt_CBC(message.encode(), password))
    return message_encrypted


def decrypt(message, password):
    password = password.to_bytes(32, 'big')
    message_decrypted = str(zpp_serpent.decrypt_CBC(message, password).decode())  # было eval(message)
    return message_decrypted
