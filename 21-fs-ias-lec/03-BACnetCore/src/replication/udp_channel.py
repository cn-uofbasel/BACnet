from queue import Queue, Empty
from .channel import Channel
import socket
from threading import Thread


class UDPChannel(Channel):
    """
    This is a specific implementation of a channel, using the UDP protocol. It can be used like that
    or be seen as an example class for further channel implementations using different protocols / ways
    to transfer data.
    """

    def __init__(self, dest_ip, dest_port=6000, own_port=None):
        super().__init__()
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        if own_port is None:
            self.own_port = self.dest_port
        else:
            self.own_port = own_port
        self.input_queue = Queue()
        self.output_queue = Queue()
        # configure socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.own_port))
        self.sock.settimeout(1)
        self.send_thread = None
        self.receive_thread = None
        self.threads_running = None

    def receive(self):
        """
        This method runs in a thread which is responsible for putting all incoming messages into the input_queue.
        """
        while self.threads_running:
            try:
                data, address = self.sock.recvfrom(1024)
                if data:
                    self.input_queue.put_nowait(data)
                    print(f"received data from {address}")
            except socket.timeout:
                continue

    def send(self):
        """
        This method runs in a thread that is responsible for getting all items from the output_queue and to
        send them to the peer.
        """
        while self.threads_running:
            try:
                self.sock.sendto(self.output_queue.get(block=True, timeout=3), (self.dest_ip, self.dest_port))
            except Empty:
                print("Sendto had timeout!")
                continue

    def set_input_queue(self, q_input: Queue):
        self.input_queue = q_input

    def set_output_queue(self, q_output: Queue):
        self.output_queue = q_output

    def start(self):
        """
        Starts the threads for receiving and sending
        """
        self.threads_running = True
        self._start_send_thread()
        self._start_receive_thread()

    def stop(self):
        self.threads_running = False

    def _start_send_thread(self):
        self.send_thread = Thread(target=self.send)
        self.send_thread.start()

    def _start_receive_thread(self):
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()



