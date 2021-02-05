# import os, sys
#
# abs_dir = os.path.abspath(os.path.dirname(__file__))
# folder_ias_g7 = os.path.join(abs_dir, '..', '..', '..', '..', 'groups', '07-logStore', 'src')
# sys.path.append(folder_ias_g7)
#
# from logStore.appconn.connection import Function
#

class LogWrapper():

    def __init__(self, local_name, other_name):
        self.app = local_name + "_" + other_name
        self.pretty_app = local_name + "->" + other_name
        self.mock_list = []

    def append(self, cbor):
        print("[{}] append() -> {}".format(self.pretty_app, cbor))
        self.mock_list.append(cbor)

    def get_last(self):
        ret = self.mock_list[-1]
        print("[{}] get_last() -> {}".format(self.pretty_app, ret))
        return self.mock_list[-1]

    def get_all(self):
        print("[{}] get_all() -> {}".format(self.pretty_app, self.mock_list))
        return self.mock_list
