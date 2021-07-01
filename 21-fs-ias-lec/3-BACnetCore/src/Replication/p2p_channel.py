from channel import Channel


class P2PChannel(Channel):

    def __init__(self):
        super().__init__()

    def request_meta(self):
        pass

    def send_meta(self):
        pass

    def request_data(self):
        pass

    def send_data(self):
        pass
