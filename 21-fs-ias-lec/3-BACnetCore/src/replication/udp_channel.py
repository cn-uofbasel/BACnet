from queue import Queue
from .channel import Channel
import socket
from threading import Thread


class UDPChannel(Channel):
    """
    This is a specific implementation of a channel, using the UDP protocol. It can be used like that
    or be seen as an example class for further channel implementations using different protocols / ways
    to transfer data.
    """

    def __init__(self, dest_ip, dest_port=6000):
        super().__init__()
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.dest_port))
        self.send_thread = None
        self.receive_thread = None

    def receive(self):
        while getattr(self.receive_thread, "do_run", True):
            data, address = self.sock.recvfrom(1024)
            self.input_queue.put_nowait(data)

    def send(self):
        while getattr(self.send_thread, "do_run", True):
            self.sock.sendto(bytes(self.output_queue.get(True), "utf-8"), (self.dest_ip, self.dest_port))

    def set_input_queue(self, q_input: Queue):
        self.input_queue = q_input

    def set_output_queue(self, q_output: Queue):
        self.output_queue = q_output

    def start_send_thread(self):
        if self.send_thread is not None:
            self.send_thread = Thread(target=self.send())
            self.send_thread.start()

    def stop_send_thread(self):
        self.send_thread.do_run = False

    def start_receive_thread(self):
        if self.receive_thread is not None:
            self.receive_thread = Thread(target=self.receive())
            self.receive_thread.start()

    def stop_receive_thread(self):
        self.receive_thread.do_run = False
