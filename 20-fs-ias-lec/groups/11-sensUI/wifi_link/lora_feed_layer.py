import crypto
import feed
import binascii
import event
import pcap
import os


class Lora_Feed_Layer:

    def __init__(self):

        self.verbose = 1
        self.callback_sensor_feed = 0
        self.callback_control_feed = 0

        self.pcap_sensor = 'Sensor_Feed.pcap'
        key_sensor = 'keyfile_sensor.key'
        [self.sensor_feed,self.sensor_fid,self.sensor_signer] = self.create_feed(0,key_sensor,self.pcap_sensor)
        self.pcap_control = 'Control_Feed.pcap'
        key_control = 'keyfile_control.key'
        [self.control_feed,self.control_fid,self.control_signer] = self.create_feed(1,key_control,self.pcap_control)



    def get_fid_list(self):
        # get list of pcap files
        pcap_list = [self.pcap_sensor, self.pcap_control]
        fid_list = [self.sensor_fid,self.control_fid]
        return pcap_list,fid_list

    # def get_fid_list(self):
    #     # get list of pcap files
    #     files = os.listdir()
    #     pcap_list = []
    #     fid_list = []
    #     for i in files:
    #         if '.pcap' in i:
    #             pcap_list+= [i]
    #             fid_list += [pcap.get_ID(i)]
    #     return pcap_list,fid_list

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

    def get_event_seq(self, fid, nr):
        if fid == self.sensor_feed.fid:
            f = self.sensor_feed
        elif fid == self.control_feed.fid:
            f = self.control_feed
        nr_now = 0
        seq = ''
        f.seq = 0
        f.hprev = None
        for e in f:
            if not f.is_valid_extension(e):
                print("-> event " + str(f.seq+1) + ": chaining or signature problem")
            else:
                if nr_now == nr:
                    e_now = str(e.content())
            nr_now += 1
            f.seq += 1
            f.hprev = event.get_hash(e.metabits)
        return e_now

    def get_event_content(self, fid, nr):
        # reads one event from log
        if fid == self.sensor_feed.fid:
            f = self.sensor_feed
        elif fid == self.control_feed.fid:
            f = self.control_feed
        nr_now = 0
        e_now = ''
        f.seq = 0
        f.hprev = None
        for e in f:
            if not f.is_valid_extension(e):
                print("-> event " + str(f.seq+1) + ": chaining or signature problem")
            else:
                if nr_now == nr:
                    e_now = str(e.content())
            nr_now += 1
            f.seq += 1
            f.hprev = event.get_hash(e.metabits)
        return e_now

    def get_feed_content(self, fid):
        # reads content from log and returns feed
        if fid == self.sensor_feed.fid:
            f = self.sensor_feed
        elif fid == self.control_feed.fid:
            f = self.control_feed

        f.seq = 0
        f.hprev = None
        for e in f:
            if not f.is_valid_extension(e):
                print("-> event " + str(f.seq+1) + ": chaining or signature problem")
            else:
                print("-> event " + str(e.seq) + ": ok, content= " + str(e.content()))
            f.seq += 1
            f.hprev = event.get_hash(e.metabits)

        return f

    def create_event(self, fid, content):
        # event is added to feed
        if fid == self.sensor_feed.fid:
            self.sensor_feed.write(eval(content))
        elif fid == self.control_feed.fid:
            self.control_feed.write(eval(content))

    def append(self, fid, seq, e_wired):
        len_f = self.get_feed_length(fid)
        if self.verbose == 1:
            print('Length Feed:'+str(len_f))
            print('event seq:'+str(seq))

        if len_f == seq -1 :

            if fid == self.sensor_feed.fid:
                self.sensor_feed._append(e_wired)
                if (self.callback_sensor_feed):
                    self.callback_sensor_feed(self.get_event_content(fid, seq-1))
            #check if valid extension
            #callback
            elif fid == self.control_feed.fid:
                self.control_feed._append(e_wired)
                if (self.callback_control_feed):
                    self.callback_control_feed(self.get_event_content(fid, seq-1))
            #check if valid extension
            #callback
        else :
            if self.verbose == 1:
                print('Incominig event not appended')

    def subscribe_sensor_feed(self, callback):
        self.callback_sensor_feed = callback
        return True

    def subscribe_control_feed(self, callback):
        self.callback_control_feed = callback
        return True


    def create_keyfile(self,kfile):
        h = crypto.HMAC("md5")
        h.create()
        print("# new HMAC_MD5: share it ONLY with trusted peers")
        print('{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}')
        keyfile = '{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}'

        f = open(kfile, 'w')
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

    def create_feed(self,type,kfile,fname):
        #self.create_keyfile(kfile)
        #[fid,signer] = self.load_keyfile(kfile)
        #f = feed.FEED(fname, fid,signer, True)

        #hardcoded
        if type == 0:
            fid = binascii.unhexlify(b'028140a0502894ca')
            signer = crypto.HMAC("md5", binascii.unhexlify(b'1c0e070381c0e0f0783c9e4f27130904'))

        if type == 1:
            fid = binascii.unhexlify(b'4c261309040281c0')
            signer = crypto.HMAC("md5", binascii.unhexlify(b'1b0d060381c0e0f0783c1e8fc7633198'))

        #new Feeds are generatet (True)
        f = feed.FEED(fname, fid, signer, True)

        return f,fid,signer

    def delete_feed(self, fid):
        pcapf=''
        try:
            if fid == self.sensor_feed.fid:
                pcapf = self.sensor_pcap
                self.sensor_feed = 0
        except:
            if fid == self.control_feed.fid:
                pcapf = self.control_pcap
                self.control_feed = 0

        try:
            os.remove(pcapf)
            print("removed feed:"+ pcapf)
            return True
        except:
            print("couldn't remove feed "+ str(fid))
            return False

    def get_name(self,fid):
        if fid == self.sensor_fid:
            name = 'sensor feed'
            type = 0
        elif fid == self.control_fid:
            name = 'control feed'
            type = 1

        return name,type
