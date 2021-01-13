from TCPProxy import TCPProxy

tcp_stuff = TCPProxy("127.0.0.1", 13337, 22, "tcp")
tcp_stuff.start()