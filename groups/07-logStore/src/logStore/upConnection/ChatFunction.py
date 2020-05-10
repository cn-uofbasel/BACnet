from .Function import Function


class Chatfunction(Function):

    def insert_chat_msg(self, cbor):
        self.__handler.add_to_db(event_as_cbor=cbor)

    # example 'chat/chat_Id'    ->  'chat/01'
    def get_chat_since(self, application, timestamp):
        result = self.__handler.get_event_since(self, application, timestamp)
        return result

    def get_full_chat(self, application):
        return self.__handler.get_all_from_application(application)
