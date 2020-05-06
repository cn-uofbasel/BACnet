from .Function import Function


class Chatfunction(Function):

    def insert_chat_msg(self, byteObj):
        return False

    def get_chat_since(self, chatId, msgId):
        pass

    def get_full_chat(self, chatId):
        pass
