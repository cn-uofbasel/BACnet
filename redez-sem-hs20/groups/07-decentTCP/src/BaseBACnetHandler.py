class BaseHandler:

    def __init__(self):
        self.handlers = {}
        self.set_handler('init_conn',  self.handle_init_conn)
        pass

    def set_handler(self, packet_type, content):
        self.handlers[packet_type] = content

    def handle(self, event):
        if event['func'] in self.handlers.keys():
            return self.handlers[event['func']]()

    def handle_init_conn(self, content):
        print("handling init_conn")
        return True