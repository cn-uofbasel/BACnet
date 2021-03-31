if __name__ == '__main__':
    import feed_control
    import multiprocessing
    import time
    import logStore

    process = multiprocessing.Process(target=feed_control.cli)
    process.start()
    time.sleep(5)
    process.terminate()

    logMerge = LogMerge()
    from EventCreationTool import EventFactory
    dc = DatabaseConnector()
    ef = EventFactory()
    first_event = ef.first_event('chat', dc.get_master_feed_id())
    second_event = ef.next_event('chat/okletsgo', {'messagekey': 3489, 'timestampkey': 2345, 'chat_id': 745})
    pcap.write_pcap('nameofpcapfile', [first_event, second_event])
    logMerge.import_logs(os.getcwd())
    logMerge.export_logs(os.getcwd(), {ef.get_feed_id(): -1}, 10)
    events = pcap.read_pcap('nameofpcapfile.pcap')
    for event in events:
        event = Event.from_cbor(event)
        print(event.content.content[1]['master_feed'].hex())
        #2d889ace0ddfd6c4bbd5c0f486de996ff14ae948b3c236fc2607877061c4c979
        break
