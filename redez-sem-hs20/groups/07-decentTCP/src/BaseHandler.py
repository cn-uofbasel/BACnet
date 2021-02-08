class BaseHandler:
    feed_id = None
    def __init__(self):
        self.handlers = {}
        pass

    def set_handler(self, packet_type, content):
        self.handlers[packet_type] = content

    def handle_tcp(self, payload):
        pass

    def handle_bacnet(self, app, event, json):
        if event['func'] in self.handlers.keys():
            return self.handlers[event['func']](event, json)

    def set_feed_id(self, local_feed_id):
        self.feed_id = local_feed_id
