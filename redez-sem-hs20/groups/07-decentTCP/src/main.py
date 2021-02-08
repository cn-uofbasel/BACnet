from BACurlHandler import BACurlHandler
from RawTcpHandler import RawTcpHandler
from TCPProxy import TCPProxy
from log_wrapper import LogWrapper
from eventCreationTool.EventCreationTool import EventFactory
import EventHandler

path = ''

handler = RawTcpHandler()
tcp_proxy = TCPProxy("local", "remote", handler, native_tcp_app=True)
eg = EventFactory()
first_event = EventFactory.create_first_event('TcpMessage/Init', {'test': 123})
egt = EventFactory(first_event)
eh = EventHandler(egt)
eh.add_event('test/test', {'message': 123})
eh.add_event('1/1', {1: 1})
list = eh.read_pcap(path)
print(eh.getEventContent(list[1]))
