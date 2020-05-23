import hashlib
import hmac
import nacl.encoding
import nacl.signing
import nacl.exceptions
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'C:/Users/patri/Desktop/BACnet/groups/13-sneakernet/code')
#from BACnetstuff import pcap
from BACnetstuff import Event
from BACnetstuff import crypto
#import DB
import time
import cbor2
SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
HASH_INFO = {'sha256': 0}


def from_cbor(event):  # Read in an Event from cbor format (parameter is bytes()), creates a new Event object
    meta, signature, content = cbor2.loads(event)
    meta = Meta.from_cbor(meta)
    content = Content.from_cbor(content)
    return Event(meta, signature, content)

def __save_file(path, bytes):
    file = open(path + ".pcap", "wb")
    file.write(bytes)
    file.close()

def read_pcap(path_to_file):
    packets_list = []
    swap_byte_order = False
    file = open(path_to_file, "rb")
    magic_number = file.read(4)
    if magic_number == bytes.fromhex("4d3cb2a1") or magic_number == bytes.fromhex("d4c3b2a1"):
        swap_byte_order = True
    file.read(20)
    timestamp = file.read(8)
    while timestamp != b'':
        packet_length = bytearray(file.read(4))
        if swap_byte_order:
            packet_length.reverse()
        packet_length = int.from_bytes(bytes(packet_length), 'big')
        file.read(4)
        next_event = file.read(packet_length)
        if swap_byte_order:
            tmp_arr = bytearray(next_event)
            for i in range(len(tmp_arr), step=4):
                tmp_arr[i], tmp_arr[i + 1], tmp_arr[i + 2], tmp_arr[i + 3] = tmp_arr[i + 3], tmp_arr[i + 2], tmp_arr[
                    i + 1], tmp_arr[i]
            next_event = bytes(tmp_arr)
        packets_list.append(next_event)
        timestamp = file.read(8)
    file.close()
    return packets_list

def write_pcap(path_to_file, list_of_events):
    file_bytes = 0xa1b23c4d.to_bytes(4, 'big') + \
                 (2).to_bytes(2, 'big') + \
                 (4).to_bytes(2, 'big') + \
                 (0).to_bytes(4, 'big') + \
                 (0).to_bytes(4, 'big') + \
                 (131071).to_bytes(4, 'big') + \
                 (147).to_bytes(4, 'big')
    maximum_bytes = 131071
    current_payload = 0
    list_of_processed_events = []
    for event in list_of_events:
        event_byte_length = len(event)
        while event_byte_length % 4 != 0:
            event += (0).to_bytes(1, 'big')
            event_byte_length += 1
        if event_byte_length > maximum_bytes:
            continue
        if current_payload + event_byte_length > maximum_bytes:
            write_pcap(path_to_file + '0', list(set(list_of_events) - set(list_of_processed_events)))
            __save_file(path_to_file, file_bytes)
            return
        current_payload += event_byte_length
        list_of_processed_events.append(event)
        timestamp = time.time_ns()
        time_sec = int(timestamp / 1000000000)
        time_nano = timestamp - time_sec * 1000000000
        event_header = time_sec.to_bytes(4, 'big') + \
                       time_nano.to_bytes(4, 'big') + \
                       len(event).to_bytes(4, 'big') + \
                       len(event).to_bytes(4, 'big')
        file_bytes += event_header + event
    __save_file(path_to_file, file_bytes)


class LogMerge:

    def export_logs(self, path_to_pcap_folder, dict_feed_id_current_seq_no, maximum_events_per_feed_id):
        for feed_id, current_seq_no in dict_feed_id_current_seq_no.items():
            event_list = []
            current_seq_no += 1
            next_event = DB.get_event(feed_id, current_seq_no)
            while next_event is not None and len(event_list) < maximum_events_per_feed_id:
                event_list.append(next_event)
                current_seq_no += 1
                next_event = DB.get_event(feed_id, current_seq_no)
            write_pcap(path_to_pcap_folder + "/" + str(feed_id).split("'")[1] + "_v", event_list)

    def import_logs(self, paths_of_pcap_files):
        list_of_cbor_events = []
        list_of_events = []
        list_of_feed_ids = []
        for path in paths_of_pcap_files:
            list_of_cbor_events.extend(read_pcap(path))
        for event in list_of_cbor_events:
            list_of_events.append(from_cbor(event))
        for event in list_of_events:
            if event.meta.feed_id not in list_of_feed_ids:
                list_of_feed_ids.append(event.meta.feed_id)
        for feed_id in list_of_feed_ids:
            most_recent_seq_no = self.__get_most_recent_seq_no(feed_id, list_of_events)
            db_seq_no = DB.get_current_seq_no(feed_id)
            if db_seq_no == -1:
                self.__verify_and_add_logs(0, feed_id, list_of_events)
            elif most_recent_seq_no <= db_seq_no:
                return
            else:
                self.__verify_and_add_logs(db_seq_no + 1, feed_id, list_of_events)

    def __get_most_recent_seq_no(self, feed_id, list_of_events):
        most_rec_seq_no = -1
        for event in list_of_events:
            if event.meta.feed_id == feed_id and most_rec_seq_no < event.meta.seq_no:
                most_rec_seq_no = event.meta.seq_no
        return most_rec_seq_no

    def __verify_and_add_logs(self, start_seq_no, feed_id, list_of_events):
        list_of_new_events = []
        for event in list_of_events:
            if event.meta.seq_no >= start_seq_no:
                list_of_new_events.append(event)
        if start_seq_no == 0:
            prev_event = None
        else:
            prev_event = event.from_cbor(DB.get_current_event(feed_id))
        while list_of_new_events:
            event_with_lowest_seq_no = self.__get_event_with_lowest_seq_no_from_list(list_of_new_events)
            if self.__verify_event(event_with_lowest_seq_no, prev_event):
                DB.add_event(feed_id, event_with_lowest_seq_no.meta.seq_no, event_with_lowest_seq_no.get_as_cbor())
            else:
                return
            prev_event = event_with_lowest_seq_no
            list_of_new_events.remove(prev_event)

    def __get_event_with_lowest_seq_no_from_list(self, list_of_events):
        if not list_of_events:
            return None
        lowest_seq_no = list_of_events[0].meta.seq_no
        for event in list_of_events:
            if event.meta.seq_no < lowest_seq_no:
                lowest_seq_no = event.meta.seq_no
        for event in list_of_events:
            if event.meta.seq_no == lowest_seq_no:
                return event
        return None

    def __verify_event(self, event, previous_event):
        if previous_event is not None:
            previous_hash_type, hash_of_previous = event.meta.hash_of_prev
            prev_meta_as_cbor = previous_event.meta.get_as_cbor()
            if previous_event.meta.feed_id != event.meta.feed_id:
                return False
            if event.meta.seq_no - 1 != previous_event.meta.seq_no:
                return False
            if not(previous_hash_type == 0 and hashlib.sha256(prev_meta_as_cbor).hexdigest() == hash_of_previous):
                return False

        content_hash_type, hash_of_content = event.meta.hash_of_content
        signature_identifier = event.meta.signature_info
        signature = event.signature

        content = event.content.get_as_cbor()
        meta_as_cbor = event.meta.get_as_cbor()

        if not(content_hash_type == 0 and hashlib.sha256(content).hexdigest() == hash_of_content):
            return False

        if signature_identifier == 0:
            verification_key = nacl.signing.VerifyKey(event.meta.feed_id, encoder=nacl.encoding.HexEncoder)
            try:
                verification_key.verify(meta_as_cbor, signature)
            except nacl.exceptions.BadSignatureError:
                return False
        elif signature_identifier == 1:
            secret_key = DB.get_secret_hmac_key(event.meta.feed_id)
            if secret_key is None:
                return False
            generated_signature = hmac.new(secret_key, meta_as_cbor, hashlib.sha256).hexdigest()
            if signature != generated_signature:
                return False
        else:
            return False

        return True


class Content:

    # create content from scratch from identifier and parameter dictionary as specified in BACnet documentation
    def __init__(self, identifier, parameters):
        self.content = [identifier, parameters]

    @classmethod
    def from_cbor(cls, content):  # Read in a Content() object from cbor format
        identifier, parameters = cbor2.loads(content)
        return Content(identifier, parameters)

    def get_as_cbor(self):  # Get the Content cbor encoded (as bytes() python object)
        return cbor2.dumps(self.content)



class Meta:

    # Create the Meta() object from scratch (for example if you create a new event)
    def __init__(self, feed_id, seq_no, hash_of_prev, signature_info, hash_of_content):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.hash_of_prev = hash_of_prev
        self.signature_info = signature_info
        self.hash_of_content = hash_of_content

    @classmethod
    def from_cbor(cls, meta):  # Read in a Meta() object from cbor format
        feed_id, seq_no, hash_of_prev, signature_info, hash_of_content = cbor2.loads(meta)
        return Meta(feed_id, seq_no, hash_of_prev, signature_info, hash_of_content)

    def get_as_cbor(self):  # Get the cbor encoded version of the meta object
        return cbor2.dumps([self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content])

'''
from Event import Meta
from Event import Content

if __name__ == "__main__":

    logMerge = LogMerge()

    #get_current_seq_no(feed_id): integer seq_no (-1 if no such feed id exists)
    #get_current_event(feed_id): event as cbor
    #add_event(feed_id, seq_no, event)
    #secret_key = DB.get_secret_hmac_key(feed_id) (None if no key saved)
    #next_event = DB.get_event(feed_id, seq_no)

    content = Content('whateverappname/whatevercommand', {'somekey': 'somevalue', 'someotherkey': 753465734265})
    hoc = hashlib.sha256(content.get_as_cbor()).hexdigest()
    signing_key = nacl.signing.SigningKey.generate()
    verify_key_hex = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder)
    print(verify_key_hex)
    meta_data = Meta(verify_key_hex, 0, None, 'ed25519', ('sha256', hoc))
    signature = signing_key.sign(meta_data.get_as_cbor())._signature
    event = Event(meta_data, signature, content)

    meta_data_two = Meta(verify_key_hex, 1, ('sha256', hashlib.sha256(meta_data.get_as_cbor()).hexdigest()), 'ed25519', ('sha256', hoc))
    signature = signing_key.sign(meta_data_two.get_as_cbor())._signature
    event_two = Event(meta_data_two, signature, content)

    print(logMerge._LogMerge__verify_event(event, None))

    #verify_key = nacl.signing.VerifyKey(verify_key_hex,

    #                                    encoder=nacl.encoding.HexEncoder)
    #try:
    #    unsigned_message = verify_key.verify(signed_message, signature)
    #    #unsigned_message = verify_key.verify(signed)
    #    print(unsigned_message)
    #    print(type(unsigned_message))
    #    metadata_extr = Meta(unsigned_message)
    #    print(metadata_extr.seq_no)
    #except nacl.exceptions.BadSignatureError:
    #    print("signature was wrong")
'''