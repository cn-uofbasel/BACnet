from .connection import Function


class ChatFunction(Function):
    """Connection to the group chat to insert and output the chat elements"""

    def __init__(self):
        super(ChatFunction, self).__init__()

    def insert_chat_msg(self, cbor):
        """adds a new chat element as cbor

        @:parameter event: The new cbor event to be added
        @:returns 1 if successful, -1 if any error occurred
        """
        self.insert_event(cbor)

    def get_chat_since(self, timestamp, chat_id):
        """returns all elements which have a higher timestamp and the correct chat id

        @:parameter timestamp: Everything from that time will be returned
        @:parameter chat_id: Everything with the right chat_id will be returned
        @:returns a list with the chat message and the timestamp of the message if successful, None if any error occurred
        """
        return self._handler.get_event_since('chat', timestamp, chat_id)

    def get_full_chat(self, chat_id):
        """returns all chat elements with the correct chat id

        @:parameter chat_id: Everything with the right chat_id will be returned
        @:returns a list of all messages with the corresponding chat_id if successful, None if any error occurred
        """
        return self._handler.get_all_chat_msgs('chat', chat_id)
