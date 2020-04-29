from .SqLiteConnector import SqLiteConnector
from functions.Singleton import Singleton


class ByteArrayHandler(metaclass=Singleton):

    def __init__(self):
        self.__connector = SqLiteConnector()

    def init_byte_obj_table(self):
        return False

    def retrieve_byte_array(self, hashref):
        pass

    def insert_byte_array(self, byteArray):
        return False