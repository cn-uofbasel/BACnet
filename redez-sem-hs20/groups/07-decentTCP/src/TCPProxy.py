from threading import Thread
import socket
import cbor2
import time

from BaseHandler import BaseHandler
from TCPClient import TCPClient
from logStore.funcs.event import Event, Content
from logStore.transconn.database_connector import DatabaseConnector
from logSync import database_transport as transport  # for databases
from logSync.database_sync import verify_validation

from log_wrapper import LogWrapper

BUFFER_SIZE = 8192


class TCPProxy():
    def __init__(self, local_feed_id, remote_feed_id,
                 handler: BaseHandler, synchronize_in_port=25565, synchronize_out_port=25566, native_tcp_app=True):
        if native_tcp_app:
            handler.set_feed_id(local_feed_id)
        self.sync_local = Server(self, synchronize_out_port, local_feed_id, handler)  # logSync-Server Thread
        self.sync_remote = Client(self, synchronize_in_port, remote_feed_id, handler)  # logSync-Client Thread

        self.sync_local.start()
        self.sync_remote.start()


class Server(Thread):

    def __init__(self, proxy: TCPProxy, port, feed_id, handler: BaseHandler):
        super().__init__()
        self.port = int(port)
        self.feed_id = feed_id
        self.handler = handler
        self.proxy = proxy
        # Create the socket and bind to host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setblocking(False)
        self.__event_list_to_send = []
        self.running = True

    def broadcast_diff(self):
        self.dbg("start Broadcast ({})".format(self.port))
        connected = True
        address = None
        while connected:
            self.socket.sendto(b'decent_tcp_init_broadcast', ('<broadcast>', self.port))
            time.sleep(1)
            try:
                info_request, address = self.socket.recvfrom(BUFFER_SIZE)  # 4
                if info_request == str.encode('decent_tcp_request_diff'):
                    self.socket.sendto(transport.get_i_have_list(), address)  # 4
                    self.dbg("snd: 'I_HAVE_LIST'")
                    connected = False
            except:
                pass

        self.socket.setblocking(True)
        i_want_list = self.socket.recv(BUFFER_SIZE)
        self.dbg("recv: 'I_WANT_LIST'")
        self.socket.sendto(transport.get_event_list(i_want_list), address)  # 11
        self.dbg("snd: 'EVENT_LIST'")
        self.socket.close()

    """
    This is a list of the needed extensions of log files that have to be sent (already serialized)! 
    This method can be used by the other groups to transfer the information as they have to (QR code, etc...)
    """

    def get_packet_to_send_as_bytes(self):
        return self.__event_list_to_send

    def run(self):
        while self.running:
            self.broadcast_diff()

    def stop(self):
        self.running = False

    def dbg(self, txt):
        print("[{}] {}".format(self.feed_id, txt))


class Client(Thread):
    buffSize = 8192

    def __init__(self, proxy: TCPProxy, port, feed_id, handler: BaseHandler):
        super().__init__()
        self.feed_id = feed_id
        self.handler = handler
        self.proxy = proxy
        # Create the UDP socket and request the log extensions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 2
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(('', int(port)))
        self.running = True

    def update_log(self):
        broadcasting = True
        address = None
        while broadcasting:
            self.dbg("wait for Broadcast")
            msg, address = self.socket.recvfrom(BUFFER_SIZE)
            if msg == b'decent_tcp_init_broadcast':
                self.dbg("requesting the diff list.")
                self.socket.sendto(str.encode('decent_tcp_request_diff'), address)  # 3
                broadcasting = False

        self.__received_package_as_events = []
        packet, self.__list_of_needed_extensions = transport.get_i_want_list(self.socket.recv(BUFFER_SIZE))
        self.dbg("recv: 'I_HAVE_LIST'")

        self.socket.sendto(packet, address)  # 8
        self.dbg("snd: 'I_WANT_LIST'")

        event_list = self.socket.recv(BUFFER_SIZE)  # 11
        self.dbg("recv: 'EVENT_LIST'")

        if not cbor2.dumps(event_list):
            self.dbg("up-to-date")

        self.__received_package_as_events = event_list
        self.socket.close()

        received_extensions = cbor2.loads(self.__received_package_as_events)
        dc = DatabaseConnector()
        for i, val in enumerate(self.get_list_of_needed_extensions()):
            appended_events_list = received_extensions[i]
            # Check if valid
            if verify_validation(val, appended_events_list[0]):
                for ev in appended_events_list:
                    app_name = cbor2.loads(ev)
                    app_name = cbor2.loads(app_name[2])
                    app_name = str(app_name[0]).split("/")
                if dc.check_incoming(val[0], app_name[0]):
                    print(app_name)
                    dc.add_event(ev)
                    a = Event.from_cbor(ev)
                    (app, identifier) = a.content[0].split('/')
                    json = a.content[1]
                    response = self.handler.handle_bacnet(app, identifier, json)
                    #TODO: write back response to BACnet
            else:
                print("The extension is not valid! Sync of one received feed is not possible.")


    """
    This is a list of the received log extensions that can be appended to the files. for use in database_sync
    """

    def get_packet_to_receive_as_bytes(self):
        return self.__received_package_as_events

    def get_list_of_needed_extensions(self):
        return self.__list_of_needed_extensions

    def run(self):
        while self.running:
            self.update_log()

    def stop(self):
        self.running = False

    def dbg(self, txt):
        print("[{}] {}".format(self.feed_id, txt))
