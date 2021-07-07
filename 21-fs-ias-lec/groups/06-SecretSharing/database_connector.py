from logStore.appconn import connection
import EventCreationTool
import json, os


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class RequestHandler:
    def __init__(self):
        self.num = 0
        self.logged_in = False
        self.event_factory = None
        self.db_connection = connection.Function()
        print(f"Host Master Feed Id: {self.db_connection.get_host_master_id()}")
        self.load_user()

    def load_user(self):
        script_dir = os.path.dirname(__file__)
        rel_path = "data/keys/user.json"
        abs_path = os.path.join(script_dir, rel_path)

        if os.path.isfile(abs_path):
            with open(abs_path, "r") as fd:
                user_dict = json.loads(fd.read())
                feed_id = bytes.fromhex(user_dict["feed_id"])
                username = user_dict["username"]
                print(f"Logged in as: {username}")
                self.event_factory = EventCreationTool.EventFactory(last_event=self.db_connection.get_current_event(feed_id),
                                                                    path_to_keys=os.path.join(script_dir, "data/keys/"),
                                                                    path_to_keys_relative=False)
                self.logged_in = True

    def next(self):
        self.num += 1
        print(self.num)

    def is_logged_in(self):
        return self.logged_in

    def create_user(self, username):
        print("creating new user")
        script_dir = os.path.dirname(__file__)
        rel_path = "data/keys/user.json"
        abs_path = os.path.join(script_dir, rel_path)
        self.event_factory = EventCreationTool.EventFactory()
        feed_id = self.event_factory.get_feed_id()
        first_event = self.event_factory.first_event("chat", self.db_connection.get_host_master_id())
        print(first_event)
        if self.db_connection.insert_event(first_event) == -1:
            print("Inserting first event failed")
        print(f"feed_id:{feed_id} with username: {username} created")
        os.replace(script_dir +"/"+  feed_id.hex() + ".key", os.path.join(script_dir,"data/keys/" + feed_id.hex() + ".key"))
        with open(abs_path, "w") as fd:
            user_dict = {
                "username": username,
                "feed_id": feed_id.hex()
            }
            fd.write(json.dumps(user_dict, indent=4))
