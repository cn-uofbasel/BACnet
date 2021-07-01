from enum import Enum


class OperationModes(Enum):
    AUTOSYNC = 1
    MANUAL = 2


class ComLink:

    def __init__(self, channels, operation_mode: OperationModes):
        self.channels = channels
        self.operation_mode = operation_mode

        if operation_mode == OperationModes.AUTOSYNC:
            self.__autosync(1000)

    def sync_masters(self):
        pass

    def sync_content(self):
        pass

    def sync_all(self):
        pass

    def import_masters(self):
        pass

    def import_content(self):
        pass

    def import_all(self):
        pass

    def export_masters(self):
        pass

    def export_content(self):
        pass

    def export_all(self):
        pass

    def check_subscribed(self):
        pass

    def __parse_next_input(self):
        pass

    def __autosync(self, interval):
        pass
