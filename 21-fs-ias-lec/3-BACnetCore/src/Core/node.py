

class Node:

    def __init__(self, operation_mode, channels, storage=None):
        self.operation_mode = operation_mode
        self.channels = channels
        self.storage = storage

    def get_master(self):
        pass

    def get_channels(self):
        pass

    def add_channel(self):
        pass

    def get_storage(self):
        pass

    def get_com_link(self):
        pass

    def remove_channel(self):
        pass

    def shutdown(self):
        pass
