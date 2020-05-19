from .connection import Function


class ChatFunction(Function):

    def __init__(self):
        super(ChatFunction, self).__init__()

    def insert_chat_msg(self, cbor):
        self.insert_event(cbor)

    def get_chat_since(self, application, timestamp, feed_Id, chat_id):
        result = self.__handler.get_event_since(application, timestamp, feed_Id, chat_id)
        return result

    def get_full_chat(self, application, feed_Id, chat_id):
        return self.__handler.get_all_chat_msgs('chat', chat_id)

    def get_last_event(self, feed_id):
        return super().get_event(feed_id)