
from BackEnd import gate
from os import urandom

if __name__ == '__main__':
    encryptor = gate.Encryptor()
    secret = urandom(16)
    encrypted_secret, iv = encryptor.encrypt_secret("p24Hz7247%", secret)
    print("Secret: {}, Length: {}".format(secret, len(secret)))
    print("E(S):{}, Length: {}, IV: {}".format(encrypted_secret, len(encrypted_secret), iv))
