from TCPProxy import TCPProxy
from log_wrapper import LogWrapper


my_log_wrapper = LogWrapper("A", "SSH")
other_log_wrapper = LogWrapper("SSH", "A")

my_log_wrapper.append("lel")
my_log_wrapper.append("l1")
my_log_wrapper.append("l3")
my_log_wrapper.get_last()
my_log_wrapper.append("l2")
my_log_wrapper.get_all()
other_log_wrapper.append("lel")
other_log_wrapper.append("l1")
other_log_wrapper.append("l3")
other_log_wrapper.get_last()
other_log_wrapper.append("l2")
other_log_wrapper.get_all()


tcp_proxy = TCPProxy("SSH", "A", remote_log=my_log_wrapper, local_log=other_log_wrapper)