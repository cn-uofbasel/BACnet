#!/usr/bin/env python3

""" A simple beacon transmitter class to send a 1-byte message (0x0f) in regular time intervals. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

# usage:
# python p2p_send.py -f 433 -b BW125 -s 12

import sys
from time import sleep

sys.path.insert(0, '..')
from BacNet_SX127x.LoRa import *
from BacNet_SX127x.LoRaArgumentParser import LoRaArgumentParser
from BacNet_SX127x.board_config import BOARD
import queue
import logging as log

# This class provides the connection to the LoRa Gateway Sx127x
# an manages the incoming and outgoing messages
# To send a message this class holds an txQueue.
# Every message in this Queue, will be send automatically to the Lora Hardware
# To receive a message this class holds an rxQueue.
# Every message received, will be forwarded to this Queue
# To register these Queues, this Class provides an registerRx and registerTx method
# Further this class check weather the spi bus is still alive
class LinkLayer(LoRa):
    tx_counter = 0
    rx_counter = 0
    # if true, detailed messages will be printed
    verbose = False
    args = None
    #send and receive queue references
    rxQueue: queue.Queue = None
    txQueue: queue.Queue = None

    # init the driver
    def __init__(self, verbose=False):
        super(LinkLayer, self).__init__(verbose)
        # sleep mode before change mapping
        self.set_mode(MODE.SLEEP)
        # set mapping to receive
        self.set_dio_mapping([1, 0, 0, 0, 0, 0])
        self.verbose = verbose

    # Here happens the Magic
    # This Event fires if there is a rx package
    def on_rx_done(self):

        # indicate rx
        BOARD.led_on()
        log.info("Rx Done Enter")
        self.clear_irq_flags(RxDone=1)

        self.rx_counter += 1

        # read the bytestream from loradriver
        byteStream = self.read_payload(nocheck=True)
        # parse bytestream to string
        data = ''.join([chr(c) for c in byteStream])
        log.info(data)
        # add string to queue
        self.rxQueue.put(data)

        # reset rx pointer
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        # start listening again
        self.set_mode(MODE.RXCONT)

    # set the led and mode after sending a message
    def on_tx_done(self):
        # Send is done
        BOARD.led_on()
        log.info("Tx Done Enter")
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)

        self.tx_counter += 1

    def on_cad_done(self):
        log.debug("\non_CadDone")
        log.debug(self.get_irq_flags())

    def on_rx_timeout(self):
        log.debug("\non_RxTimeout")
        log.debug(self.get_irq_flags())

    def on_valid_header(self):
        log.debug("\non_ValidHeader")
        log.debug(self.get_irq_flags())

    def on_payload_crc_error(self):
        log.debug("\non_PayloadCrcError")
        log.debug(self.get_irq_flags())

    def on_fhss_change_channel(self):
        log.debug("\non_FhssChangeChannel")
        log.debug(self.get_irq_flags())

    # start the driver
    def start(self):
        log.info("start")
        self.tx_counter = 0
        BOARD.led_on()
        log.info(self.getModeString())
        # Force mode Standby
        self.set_mode(MODE.STDBY)

        # driver main routine
        # waits on rec message, till there is something to send
        while True:
            sleep(1)
            # If communication to board is ok
            if self.spiHearthbeat():
                log.info(f"Alive {self.getModeString()}")

                # There is something to send
                if not self.txQueue.empty():
                    # take sting object from queue
                    stringToSend = self.txQueue.get()
                    # parse string to bytestream
                    byteStream = [int(hex(ord(c)), 0) for c in stringToSend]
                    # Set the pin mapping to tx
                    # this will only be done if there is something to send
                    # and only for a short time period
                    # fires the on_tx_done event
                    self.set_dio_mapping([1, 0, 0, 0, 0, 0])
                    # write bytestream into loradriver
                    self.write_payload(byteStream)
                    # Send
                    self.set_mode(MODE.TX)
                    # wait till message is sent
                    while self.isMode(MODE.TX):
                        log.info(self.getModeString())
                        sleep(1)

                else:
                    # if there is nothing to send, map pins to rx
                    # this is the normal state
                    # fires the on_rx_done event
                    self.set_dio_mapping([0, 0, 0, 0, 0, 0])
                    if not self.isMode(MODE.RXCONT):
                        self.set_mode(MODE.SLEEP)
                        self.reset_ptr_rx()
                        self.set_mode(MODE.RXCONT)
            # if there is an error in board communication
            # try restart
            else:
                log.warning("dead")
                BOARD.setup()

    # Setup the hardware config for LoRa Gateway (See LoraArgumentParser.py)
    def setup(self, args):
        self.args = args
        self.set_pa_config(pa_select=1)
        # lora.set_rx_crc(True)
        # lora.set_agc_auto_on(True)
        # lora.set_lna_gain(GAIN.NOT_USED)
        # lora.set_coding_rate(CODING_RATE.CR4_6)
        # lora.set_implicit_header_mode(False)
        # lora.set_pa_config(max_power=0x04, output_power=0x0F)
        # lora.set_pa_config(max_power=0x04, output_power=0b01000000)
        # lora.set_low_data_rate_optim(True)
        # lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
        log.info(self)
        # assert(lora.get_lna()['lna_gain'] == GAIN.NOT_USED)
        assert (self.get_agc_auto_on() == 1)

    # Register the Rx Queue for outgoing messages
    def registerRx(self, qRx: queue.Queue):
        self.rxQueue = qRx

    # Register the Tx Queue for incoming messages
    def registerTx(self, qTx: queue.Queue):
        self.txQueue = qTx

    # Shutdown the LoRa board
    def shutdown(self):
        self.set_mode(MODE.SLEEP)
        log.info(self)
        BOARD.teardown()

    # Dict for Mode to string translation
    mode_lookup = {0x80: "SLEEP", 0x82: "STDBY", 0x81: "FSTX", 0x84: "TX", 0x83: "FSRX", 0x85: "RXCONT",
                   0x86: "RXSINGLE", 0x87: "CAD", 0x01: "FSK_STDBY"}

    # Reads tha actual operating mode of LoRa board
    def getModeString(self):
        return self.mode_lookup.get(self.get_mode() | 0x80)

    # Checks if the mode is the operating mode
    def isMode(self, mode):
        return (self.get_mode() | 0x80) == mode

    # Returns weather the board is alive or notg
    def spiHearthbeat(self):
        return self.isSpiAlive()
