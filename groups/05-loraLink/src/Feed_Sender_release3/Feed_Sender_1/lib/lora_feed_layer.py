import crypto
import feed
import binascii
import event
import pcap


class Lora_Feed_Layer:

    def __init__(self):
        self.sensor_fid = binascii.unhexlify(b'028140a0502894ca')
        self.sensor_signer = crypto.HMAC("md5", binascii.unhexlify(b'1c0e070381c0e0f0783c9e4f27130904'))

        self.control_fid = binascii.unhexlify(b'4c261309040281c0')
        self.control_signer = crypto.HMAC("md5", binascii.unhexlify(b'1b0d060381c0e0f0783c1e8fc7633198'))


        self.sensor_feed = feed.FEED("Sensor_Feed.pcap", self.sensor_fid, None, True)

        self.control_feed = feed.FEED("Control_Feed.pcap", self.control_fid, self.control_signer, True)

        self.test_callback = 0

    def get_sensor_feed_fid(self):
        return self.sensor_fid

    def get_control_feed_fid(self):
        return self.control_fid

    def get_feed_length(self, fid):
        if fid == self.sensor_feed.fid:
            return len(self.sensor_feed)
        elif fid == self.control_feed.fid:
            return len(self.control_feed)
        return 0

    def get_wired_event(self, fid, nr):
        if fid == self.sensor_feed.fid:
            for e in self.sensor_feed:
                if (e.seq == nr):
                    e_trans = e
                    signature = e_trans.get_metabits(self.sensor_signer.get_sinfo())
                    e_wired = e_trans.to_wire(signature)
                    return e_wired

        elif fid == self.control_feed.fid:
            for e in self.control_feed:
                if (e.seq == nr):
                    e_trans = e
                    signature = e_trans.get_metabits(self.control_signer.get_sinfo())
                    e_wired = e_trans.to_wire(signature)
                    return e_wired

        return 0

    def get_event_content(self, fid, nr):
        return 0

    def create_event(self, fid, content):
        if fid == self.sensor_feed.fid:
            self.sensor_feed.write(eval(content))
        elif fid == self.control_feed.fid:
            self.content_feed.write(eval(content))

    def append(self, fid, e_wired):
        if fid == self.sensor_feed.fid:
            self.sensor_feed._append(e_wired)
            if (self.callback):
                self.callback(e_wired)
            #check if valid extension
            #callback
        elif fid == self.control_feed.fid:
            self.control_feed._append(e_wired)
            #check if valid extension
            #callback

    def subscribe(self, callback, fid):
        self.callback = callback
        return True

    def unsubscribe(self, callback, fid):
        return True


    def create_keyfile(self):
        h = crypto.HMAC("md5")
        h.create()
        print("# new HMAC_MD5: share it ONLY with trusted peers")
        print('{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}')
        keyfile = '{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}'

        f = open('secret.key', 'w')
        f.write(keyfile)
        f.close()

    def load_keyfile(self, fn):
        with open(fn, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'hmac_md5':
            #fid = bytes.fromhex(key['feed_id'])
            fid = binascii.unhexlify(key['feed_id'])
            #signer = crypto.HMAC256(bytes.fromhex(key['private']))
            signer = crypto.HMAC("md5", binascii.unhexlify(key['private']))
        return fid, signer
