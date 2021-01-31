import struct


def h_noop(data):
    return data

handlers = {
    0x0000: h_noop
}


def parse(data, port, proxy_type, proxy_name):
    if proxy_type != 'client':
        return
    if len(data) < 2:
        return
    print("{}".format(data[0:2].hex()))
    packet_id = struct.unpack(">H", data[0:2])[0]
    if packet_id not in handlers:
        print("[{}][{}:{}] {}".format(proxy_name, proxy_type, port, data.hex()))
    handlers.get(packet_id, h_noop)(data[2:])

