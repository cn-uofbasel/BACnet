class Event:
    __timestamp = 0
    __feed_id = 0
    __hash_ref = None
    __data = None

    def __init__(self, timestamp, feed_id, hash_ref, data):
        self.__timestamp = timestamp
        self.__feed_id = feed_id
        self.__hash_ref = hash_ref
        self.__data = data

    def get_timestamp(self):
        return self.__timestamp

    def get_feed_id(self):
        return self.__feed_id

    def get_hash_ref(self):
        return self.__hash_ref

    def get_data(self):
        return self.__data


class Feed:
    __events = None
    __feed_id = 0

    def __init__(self, feed_id):
        self.__feed_id = feed_id
        self.__events = []

    def add_event(self, event):
        self.__events.append(event)
