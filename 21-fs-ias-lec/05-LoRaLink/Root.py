from BacNet_SX127x.LoRa import *
from BacNet_SX127x.LoRaArgumentParser import LoRaArgumentParser
from BacNet_SX127x.board_config import BOARD
from linklayer import LinkLayer
import threading
import queue
import logging as log
from transport import TransportLayer
from application import ApplicationLayer


def loggerSetup():
    log.basicConfig(format='%(levelname)s:%(message)s', level=log.WARNING)
    log.debug("debug is active")
    log.info("info is active")
    log.warning("warning is active")
    log.error("error is active")
    log.critical("critical is active")

# Lora Thread
def startLoraThread(args,qRx,qTx):
    # Setup GPIO
    BOARD.setup()
    # Instance of Lora driver
    lora = LinkLayer(verbose=False)
    args = parser.parse_args(lora)
    lora.setup(args)
    lora.registerRx(qRx)
    lora.registerTx(qTx)
    lora.start()

def startTransportLayer(msg_Rx, msg_Tx, qRx, qTx):
    transLayer = TransportLayer()
    transLayer.register_msg_Rx(msg_Rx)
    transLayer.register_msg_Tx(msg_Tx)
    transLayer.register_qRx(qRx)
    transLayer.register_qTx(qTx)
    transLayer.start()


def startApplicationLayer(raw_Rx, raw_Tx):
    applLayer = ApplicationLayer()
    applLayer.register_msg_Rx(raw_Rx)
    applLayer.register_msg_Tx(raw_Tx)
    applLayer.start()



def main(parser):
    # Loggers setup, choose log level in method above
    loggerSetup()
    # Create send and receive Queue
    qRx = queue.Queue()
    qTx = queue.Queue()
    q_msg_Rx = queue.Queue()
    q_msg_Tx = queue.Queue()
    # Setup sned/receive link thread
    loraThread = threading.Thread(target=startLoraThread, name="Link", args=(parser, qRx, qTx))
    # Setup Keyboard input thread (application thread)
    input_output_Thread = threading.Thread(target=startApplicationLayer, name="Application", args=(q_msg_Rx, q_msg_Tx))
    # Setup send/receive transport thread
    transportThread = threading.Thread(target=startTransportLayer, name="Transport", args=(q_msg_Rx, q_msg_Tx, qRx, qTx))
    input_output_Thread.start()
    transportThread.start()
    loraThread.start()


if __name__ == "__main__":
    # Loralink Parser setup
    # Seee BacNet_SX127x package
    parser = LoRaArgumentParser("A simple LoRa beacon")
    # Own Args
    parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
    parser.add_argument('--wait', '-w', dest='wait', default=1, action="store", type=float,
                        help="Waiting time between transmissions (default is 0s)")

    main(parser)