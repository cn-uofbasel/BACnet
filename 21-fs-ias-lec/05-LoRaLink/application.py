import queue
import threading
from datetime import datetime

class ApplicationLayer():
    """
    This class describes the input and output on the user side.

    The application layer is connected to the transport layer via two queues. It is responsible for taking user inputs
    and passing it to the transport layer. It is also responsible for printing messages supplied by the transport layer.
    It checks if the user input has the correct format and length.

    Attributes:
        msg_rx_queue (Queue): Queue that contains received messages.
        msg_tx_queue (Queue): Queue that contains output messages.
    """

    msg_rx_counter = 0
    msg_tx_counter = 0
    msg_rx_queue: queue.Queue = None
    msg_tx_queue: queue.Queue = None

    def __init__(self):
        self.log = {}

    def read_message(self):
        """
        Reads input from stdin and puts it to msg_tx_queue to send to transport layer.

        Returns:
            None
        """

        inputString = input(">> ")
        if self.check_msg_format(inputString) and self.check_data_len(inputString):
            packed_msg = self.pack_msg(inputString)
            #append to log
            self.msg_tx_queue.put(packed_msg)
        else:
            return

    def start_input_thread(self):
        """
        Starts thread for reading input from stdin.

        Returns:
            None
        """

        while True:
            self.read_message()

    def print_msg(self):
        """
        Takes message from msg_rx_queue and prints it to stdout.

        Returns:
            None
        """

        msg = self.msg_rx_queue.get()
        unpacked_msg = self.unpack_msg(msg)
        print(unpacked_msg)

    def start_output_thread(self):
        """
        Starts thread for printing messages.

        Returns:
            None
        """

        while True:
            if not self.msg_rx_queue.empty():
                self.print_msg()

    def register_msg_Rx(self, msg_qRx: queue.Queue):
        self.msg_rx_queue = msg_qRx

    def register_msg_Tx(self, msg_qTx: queue.Queue):
        self.msg_tx_queue = msg_qTx

    def pack_msg(self, msg: str) -> str:
        """
        Packs the input messages from stdin with appending the current time.

        Args:
            msg (str): Raw user input from stdin.

        Returns:
            packed: String containing <current time ; message>
        """

        now = str(datetime.now().time())
        packed = now + ";" + msg
        return packed

    def check_data_len(self, msg: str) -> bool:
        """
        Limits the maximum data length to 100.

        Args:
            msg (str): Raw user input from stdin.

        Returns:
            boolean
        """

        if len(msg) <= 100:
            return True
        else:
            print("Message to long please shorten your message!")
            return False

    def unpack_msg(self, msg: str) -> str:
        """
        Unpack message for printing to stdout.

        Args:
            msg (str): Message with prepended receiver.

        Returns:
            String: The message that is received with the correct format.
        """

        sender = msg.split(";")[0]
        data = msg.split(";")[1]
        return str("Received from " + sender + ": " + data)

    def check_msg_format(self, msg: str) -> bool:
        """
        Checks if input from stdin has correct format (<receiver;message>).

        Args:
            msg (str): Message with prepended receiver.

        Returns:
             boolean
        """

        try:
            receiver = msg.split(";")[0]
            data = msg.split(";")[1]
            return True
        except Exception:
            print("Wrong format please type like the following: receiver;msg")
            return False

    def start(self):
        """
        Starts the input and output thread.

        Returns:
            None
        """

        output_thread = threading.Thread(target= self.start_output_thread)
        output_thread.start()
        input_thread = threading.Thread(target= self.start_input_thread)
        input_thread.start()