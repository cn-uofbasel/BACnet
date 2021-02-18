import socket
import create
import color
from client import Client
from client_list import ClientList

config_path, clients_path, flag_conf = create.config_client_files()
filesystem_path, flag_fs = create.filesystem()
PORT = 65184

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return IP


if __name__ == "__main__":
    clients = ClientList()
    try:
        if flag_fs or flag_conf:
            print(color.green("Server setup complete. Restart to operate."))
            exit(0)
        IP = getIP()
        print("IP: {} | Port: {}".format(IP, PORT))
        server.bind((IP, PORT))
        server.listen(20)
        while True:
            conn, addr = server.accept()
            client = Client(conn, addr, clients_path, config_path, filesystem_path)
            clients.add(client.hash, client)
    except KeyboardInterrupt:
        clients.send_all("DEN")
