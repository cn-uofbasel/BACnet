from BACurlHandler import BACurlHandler
from TCPProxy import TCPProxy
from log_wrapper import LogWrapper



handler = BACurlHandler()
tcp_proxy = TCPProxy("local", "remote", handler, native_tcp_app=False)