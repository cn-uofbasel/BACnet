import receiveEther
import sendEther
import split
import time


def sender(packet, interface):

    #packet = get_i_have_list

    packet = split.split_data(packet)
    time.sleep(2)
    sendEther.send_len(packet, interface)

    time.sleep(4)
    sendEther.send_packet(packet, interface)


def receiver(interface):

    len = receiveEther.receive_len(interface)

    print("LEN", len)

    time.sleep(3)

    list = receiveEther.receive_list(len, interface)
    list = receiveEther.append(list)

    return list
