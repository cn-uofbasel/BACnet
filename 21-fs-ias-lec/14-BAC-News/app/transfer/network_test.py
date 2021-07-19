import socket
import scapy.all as scapy
def scan(ip):
    arp_req_frame = scapy.ARP(pdst = ip)
    #print(scapy.ls(scapy.ARP()))
    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame
    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 1, verbose = False)[0]
    result = []

    for i in range(0, len(answered_list)):
        device_name = ""
        try:
            # get device names with ip address
            hostname = socket.gethostbyaddr(answered_list[i][1].psrc)
            device_name += hostname[0]
        except socket.herror:
            # failed to resolve
            pass
        # contains (ip, mac, device name)
        client_dict = {"ip" : answered_list[i][1].psrc, "mac" : answered_list[i][1].hwsrc, "name" : device_name}
        result.append(client_dict)

    return result

def display_result(result):
    print("-----------------------------------\nIP Address\tMAC Address\t\tDevice Name\n-----------------------------------")
    for i in result:
        print("{}\t{}\t({})".format(i["ip"], i["mac"], i["name"]))



#scanned_output = scan('192.168.2.3/24')
#display_result(scanned_output)