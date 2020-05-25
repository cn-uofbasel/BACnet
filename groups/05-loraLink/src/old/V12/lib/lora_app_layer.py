import os
import sys
import crypto
from feed import FEED
import binascii
import event
import pcap
import binascii
from lora_network_layer import Gossip

#from crypto import HMACMD5

# import lopy4_cbor
# from lopy4_cbor import dumps
# from lopy4_cbor import loads
# import lopy4_hmac


class Lora_App:

    def __init__(self):

        os.remove("feed1.pcap")
        os.remove("secret1.key")

        key_file = 'secret1.key'
        pcapfile = 'feed1.pcap'
        pcapcopy = 'feed1_copy.pcap'
        new = 1
        mod = 'md5'
        nr = 4

        if new :
            self.new_key(key_file,mod)

        [fid, signer] = self.load_keyfile(key_file,mod)

        for i in range(nr) :
            feed_cont = self.f_input()
            if new :
                f = self.f_append(pcapfile,fid,signer,feed_cont,1)
                new=0
            else :
                f = self.f_append(pcapfile,fid,signer,feed_cont,0)

        #cont = self.f_read(pcapfile,fid,signer)

        #self.pcap_copy(f,signer,pcapcopy)
        #cont = self.f_read(pcapcopy,fid,signer)

        #self.gossip = Gossip()

        gossip_msg = self.get_gossip(pcapfile,fid,signer)

        e = self.check_gossip(pcapfile,fid,signer,gossip_msg)

        self.check_data(pcapfile,fid,signer,e)


        os.remove("feed1.pcap")
        #os.remove("feed1_copy.pcap")
        os.remove("secret1.key")
        print(os.listdir())

    def load_keyfile(self,fn,mod):
        with open(fn, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'hmac_'+mod :
            fid = binascii.unhexlify(key['feed_id'])
            signer = crypto.HMAC(mod,binascii.unhexlify(key['private']))
        return fid, signer

    def new_key(self,key_file,mod):
        h = crypto.HMAC(mod)
        h.create()
        print("# new "+mod+" key: share it ONLY with trusted peers")
        print('{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}')
        key = '{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}'
        f = open(key_file, 'w')
        f.write(key)
        f.close()


    def f_append(self,pcapfile,fid,signer,content,new):
        if new:
            f = FEED(pcapfile, fid, signer, True)
        else :
            f = FEED(pcapfile, fid, signer)
        f.write(eval(content))
        return f

    def f_read(self,pcapfile,fid,signer):
        f = FEED(pcapfile, fid, signer)
        f.seq = 0
        f.hprev = None
        print("Checking feed " + str(fid))
        for e in f:
            if not f.is_valid_extension(e):
                print("-> event " + str(f.seq+1) + ": chaining or signature problem")
            else:
                print("-> event " + str(e.seq) + ": ok, content= " + str(e.content()))
            f.seq += 1
            f.hprev = event.get_hash(e.metabits)
        return f

    def f_input(self):
        # add new feed
        temp = int.from_bytes(os.urandom(1), "big")
        cont = "['Temperature', '"+str(temp)+"']"
        print(cont)

        return(cont)

    def get_gossip(self,pcapfile,fid,signer):
        f = FEED(pcapfile, fid, signer)
        flen = len(f)
        print(flen)
        gossip_msg=fid+flen.to_bytes(1,'big')
        print(gossip_msg)
        return(gossip_msg)

    def check_gossip(self,pcapfile,fid,signer,gossip_msg):
        f = FEED(pcapfile, fid, signer)
        flen = len(f)
        gossip_fid = gossip_msg[0:8]
        gossip_flen = gossip_msg[8]
        print("gossip_fid:")
        print(gossip_fid)
        print(gossip_flen)
        if gossip_fid == fid :
            print("same feed id")
            #if flen == gossip_flen -1  :
            if flen >= gossip_flen :
                print("same length, prepare event")
                for e in f:
                    if e.seq == gossip_flen :
                        #Gossip.gssp_send_feed(e)
                        print("Event nr"+ str(e.seq)+" mit Inhalt: "+str(e.content()) +" is send.")
        return(e)

    def check_data(self,pcapfile,fid,signer,gossip_msg):
        f = FEED(pcapfile, fid, signer)
        flen = len(f)

        return(flen)

    def send_event(self,f,gossip_flen,flen):
        e=0
        return e

    def pcap_copy(self,f,signer,pcapcopy):
        feed_cp = FEED(pcapcopy, None, None, True)
        for e in f:
            signature = e.get_metabits(signer.get_sinfo())
            e_wired = e.to_wire(signature)
            feed_cp._append(e_wired)
