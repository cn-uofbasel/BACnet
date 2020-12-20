import SocketWrapper

class BackEndWrapper:

    def __init__(self, host, port, name):
        self.socketWrapper = SocketWrapper.SocketWrapper(host, port, name)
    
    def send(self, sendStr) -> None:
        self.socketWrapper.send(sendStr)

    def receive(self, ip, message):
        file = open(ip, "r")
        content = list()
        f1 = file.readlines()
        for x in f1:
            content.append(x)
        file.close()
        
        return content