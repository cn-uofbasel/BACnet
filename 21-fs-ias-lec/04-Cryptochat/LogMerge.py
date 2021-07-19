# The connection api for transport groups
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import hashlib
import hmac
import nacl.encoding
import nacl.signing
import nacl.exceptions
import os

from Event import Event
from PCAP import PCAP

from logStore.transconn.database_connector import DatabaseConnector
from logStore.verific.verify_insertion import Verification


SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
HASH_INFO = {'sha256': 0}


class LogMerge:

    def __init__(self):
        if not os.path.exists('cborDatabase.sqlite'):
            import feedCtrl.uiFunctionsHandler
            feedCtrl.uiFunctionsHandler.UiFunctionHandler()
        self.DB = DatabaseConnector()
        self.EV = Verification()

    def get_database_status(self):
        list_of_feed_ids = self.DB.get_all_feed_ids()
        dict_of_feed_ids_and_corresponding_sequence_numbers = {}
        for feed_id in list_of_feed_ids:
            print('feed', feed_id.hex())
            print(self.EV.check_outgoing(feed_id))
            if self.EV.check_outgoing(feed_id):
                dict_of_feed_ids_and_corresponding_sequence_numbers[feed_id] = self.DB.get_current_seq_no(feed_id)
        return dict_of_feed_ids_and_corresponding_sequence_numbers

    def export_logs(self, path_to_pcap_folder, dict_feed_id_current_seq_no, maximum_events_per_feed_id=-1):
        list_of_master_feed_ids = self.DB.get_all_master_ids()
        list_of_master_feed_ids.append(self.DB.get_master_feed_id())
        for master_feed_id in list_of_master_feed_ids:
            #print(master_feed_id)
            if master_feed_id not in dict_feed_id_current_seq_no and self.EV.check_outgoing(master_feed_id):
                event_list = []
                current_seq_no = 0
                next_event = self.DB.get_event(master_feed_id, current_seq_no)
                while next_event is not None \
                        and (maximum_events_per_feed_id == -1 or len(event_list) < maximum_events_per_feed_id):
                    event_list.append(next_event)
                    current_seq_no += 1
                    next_event = self.DB.get_event(master_feed_id, current_seq_no)
                PCAP.write_pcap(os.path.join(path_to_pcap_folder, master_feed_id.hex() + "_v"), event_list)
        for feed_id, current_seq_no in dict_feed_id_current_seq_no.items():
            if not self.EV.check_outgoing(feed_id):
                continue
            event_list = []
            current_seq_no += 1
            next_event = self.DB.get_event(feed_id, current_seq_no)
            while next_event is not None \
                    and (maximum_events_per_feed_id == -1 or len(event_list) < maximum_events_per_feed_id):
                event_list.append(next_event)
                current_seq_no += 1
                next_event = self.DB.get_event(feed_id, current_seq_no)
            PCAP.write_pcap(os.path.join(path_to_pcap_folder, feed_id.hex() + "_v"), event_list)

    def import_logs(self, path_of_pcap_files_folder):
        list_of_cbor_events = []
        list_of_events = []
        list_of_feed_ids = []
        paths_of_pcap_files = []
        for d, r, f in os.walk(path_of_pcap_files_folder):
            for file in f:
                if file.lower().endswith('.pcap'):
                    paths_of_pcap_files.append(os.path.join(d, file))
        for path in paths_of_pcap_files:
            list_of_cbor_events.extend(PCAP.read_pcap(path))
        for event in list_of_cbor_events:
            list_of_events.append(Event.from_cbor(event))
        for event in list_of_events:
            if event.meta.feed_id not in list_of_feed_ids:
                list_of_feed_ids.append(event.meta.feed_id)
        for feed_id in list_of_feed_ids:
            most_recent_seq_no = self.__get_most_recent_seq_no(feed_id, list_of_events)
            db_seq_no = self.DB.get_current_seq_no(feed_id)
            events_for_feed_id = [e for e in list_of_events if e.meta.feed_id == feed_id]
            if db_seq_no is None:
                self.__verify_and_add_logs(0, feed_id, events_for_feed_id)
            elif most_recent_seq_no <= db_seq_no:
                continue
            else:
                self.__verify_and_add_logs(db_seq_no + 1, feed_id, events_for_feed_id)

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
            prev_event = Event.from_cbor(self.DB.get_current_event(feed_id))
        while list_of_new_events:
            event_with_lowest_seq_no = self.__get_event_with_lowest_seq_no_from_list(list_of_new_events)
            if self.__verify_event(event_with_lowest_seq_no, prev_event):
                self.DB.add_event(event_with_lowest_seq_no.get_as_cbor())
                # self.DB.add_event(feed_id, event_with_lowest_seq_no.meta.seq_no, event_with_lowest_seq_no.get_as_cbor())
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

    def __verify_event(self, event, previous_event=None):
        if not self.EV.check_incoming(event.meta.feed_id, event.content.content[0].split('/')[0]):
            return False
        if previous_event is not None:
            previous_hash_type, hash_of_previous = event.meta.hash_of_prev
            prev_meta_as_cbor = previous_event.meta.get_as_cbor()
            if previous_event.meta.feed_id != event.meta.feed_id:
                return False
            if event.meta.seq_no - 1 != previous_event.meta.seq_no:
                return False
            if not(previous_hash_type == 0 and hashlib.sha256(prev_meta_as_cbor).digest() == hash_of_previous):
                return False

        content_hash_type, hash_of_content = event.meta.hash_of_content
        signature_identifier = event.meta.signature_info
        signature = event.signature

        content = event.content.get_as_cbor()
        meta_as_cbor = event.meta.get_as_cbor()

        if not(content_hash_type == 0 and hashlib.sha256(content).digest() == hash_of_content):
            return False

        if signature_identifier == 0:
            verification_key = nacl.signing.VerifyKey(event.meta.feed_id)
            try:
                verification_key.verify(meta_as_cbor, signature)
            except nacl.exceptions.BadSignatureError:
                return False
        # This code is ready to be used, but nobody is using Hmac right now.
        # elif signature_identifier == 1:
        #     secret_key = self.DB.get_secret_hmac_key(event.meta.feed_id)
        #     if secret_key is None:
        #         return False
        #     generated_signature = hmac.new(secret_key, meta_as_cbor, hashlib.sha256).digest()
        #     if signature != generated_signature:
        #         return False
        else:
            return False

        return True


if __name__ == '__main__':
    logMerge = LogMerge()
    from EventCreationTool import EventFactory
    dc = DatabaseConnector()
    ef = EventFactory()
    first_event = ef.first_event('chat', dc.get_master_feed_id())
    second_event = ef.next_event('chat/okletsgo', {'messagekey': 759432, 'timestampkey': 2345, 'chat_id': 745})
    PCAP.write_pcap('nameofpcapfile', [first_event, second_event])
    logMerge.import_logs(os.getcwd())
    logMerge.export_logs(os.getcwd(), {ef.get_feed_id(): -1}, 10)
    events = PCAP.read_pcap('nameofpcapfile.pcap')
    for event in events:
        event = Event.from_cbor(event)
        print(event.content.content[1]['master_feed'].hex())
        break
