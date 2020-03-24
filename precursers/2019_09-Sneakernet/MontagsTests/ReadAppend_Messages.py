from nacl.public import Box
import nacl.encoding


def append_messages(message, box, file="Messages.txt"):
    encrypted_message = box.encrypt(bytes(message, 'utf-8'), encoder=nacl.encoding.Base64Encoder)

    with open(file, "a") as f:
        f.write(str(nacl.encoding.Base64Encoder.encode(encrypted_message), 'utf-8'))
        f.write("\n")


def read_messages(box, file="Messages.txt"):
    print(box)
    print(file)
    with open(file, "r") as f:
        while True:
            line = str(f.readline()).replace("\n","")
            print(line)
            print("hi")
            if line is None:
                print("All Messages read")
                break
            encrypted_msg = nacl.encoding.Base64Encoder.decode(line)
            print(encrypted_msg)
            try:
                print(encrypted_msg)
            except:
                print("pass")
