# The connection api for transport groups
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import hashlib
import hmac
import nacl.encoding
import nacl.signing
import nacl.exceptions
import os
from os import walk

from Event import Event
from PCAP import PCAP

from logStore.transconn.database_connector import DatabaseConnector
from logStore.verific.verify_insertion import Verification


SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
HASH_INFO = {'sha256': 0}


class LogMerge:

    def __init__(self):
        self.DB = DatabaseConnector()
        self.EV = Verification()

    def get_database_status(self):
        list_of_feed_ids = self.DB.get_all_feed_ids()
        dict_of_feed_ids_and_corresponding_sequence_numbers = {}
        for feed_id in list_of_feed_ids:
            if self.EV.check_outgoing(feed_id):
                dict_of_feed_ids_and_corresponding_sequence_numbers[feed_id] = self.DB.get_current_seq_no(feed_id)
        return dict_of_feed_ids_and_corresponding_sequence_numbers

    def export_logs(self, path_to_pcap_folder, dict_feed_id_current_seq_no, maximum_events_per_feed_id):
        for feed_id, current_seq_no in dict_feed_id_current_seq_no.items():
            if not self.EV.check_outgoing(feed_id):
                continue
            event_list = []
            current_seq_no += 1
            next_event = self.DB.get_event(feed_id, current_seq_no)
            while next_event is not None and len(event_list) < maximum_events_per_feed_id:
                event_list.append(next_event)
                current_seq_no += 1
                next_event = self.DB.get_event(feed_id, current_seq_no)
            PCAP.write_pcap(path_to_pcap_folder + "/" + str(feed_id).split("'")[1] + "_v", event_list)

    def import_logs(self, path_of_pcap_files_folder):
        list_of_cbor_events = []
        list_of_events = []
        list_of_feed_ids = []
        paths_of_pcap_files = []
        for d, r, f in next(walk(path_of_pcap_files_folder)):
            for file in f:
                if file.lower().endswith('.pcap'):
                    paths_of_pcap_files.append(os.path.join(r, file))
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
    from ..eventCreationTool.EventCreationTool import EventFactory
    ef = EventFactory()
    ef.next_event('someapp/MASTER', {})

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