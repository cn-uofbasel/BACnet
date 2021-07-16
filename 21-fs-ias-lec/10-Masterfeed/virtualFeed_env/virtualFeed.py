#!/usr/bin/env python3

import sys
# add the lib to the module folder
sys.path.append("./lib") 


import os
import crypto 
import feed 
import event
import hashlib

def makeFiles():
	if not os.path.isdir("data"): 
		print("please run deviceHandler.py first")

	
def getLastMsg():
	print("gets the last message of the virtual feed")

#TODO: vfeed_name oder vfeed_id? vereinheitlichen
def getvfeed_name():
	file = [f for f in os.listdir("/data/virtual") if f.endswith('.key')]
	if file == []:
		print("please create a keypair first")
	vfeed_name = file[0].split('.key')[0]
	return (vfeed_name)

def getvfeed_privKey():
	vfeed_name = getvfeed_name()
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_path, 'rb') as f:
			vfeed_privKey = f.read()
	print("private key: ",vfeed_privKey)
	return vfeed_privKey

def createVirtualKeypair():
	vfeed_digestmod = "sha256"
	vfeed_h = crypto.HMAC(vfeed_digestmod)
	vfeed_h.create()
	di = '{\n  '+(',\n '.join(vfeed_h.as_string().split(','))[1:-1])+"\n}"
	key = eval(di)
	vfeed_id = key["feed_id"]
	print("vfeed_name:",key["feed_id"])
	vfeed_path = "data/virtual/" + vfeed_id + ".key"
	print("Create virtual key pair at",vfeed_path) 
	print("write key: ",key["private"])
	with open(vfeed_path, "wb") as f: 
		f.write(vfeed_h.get_private_key())
	return vfeed_id

def createStats(vfeed_name,vfeed_seq,vfeed_hprev):
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	vfeed_key_path = "data/virtual/" + vfeed_name + ".key"
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey(vfeed_name)
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

def updateStats(vfeed_name,content):
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	vfeed_key_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_stats_path, 'r') as f:
			key = eval(f.read())
			vfeed_seq = str(int(key["vfeed_seq"])+1)
	vfeed_hprev = hashlib.sha256(bytes(content, "utf-8")).hexdigest()
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey(vfeed_name)
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

def createVirtualFeed():
	print("creates new virtual Feed")
	vfeed_name = createVirtualKeypair()
	createStats(vfeed_name, "0", "None")
	return vfeed_name

def createEvent(hfeed_name,vfeed_name,message):
	
	# hfeed is the host feed of the virtual feed (vfeed)
	hfeed_key_path =  "data/"+hfeed_name+"-secret.key"
	hfeed_pcap_path = "data/"+hfeed_name+"-feed.pcap"
	vfeed_key_path =  "data/virtual/" + vfeed_name + ".key"
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	
	#host_feed read out
	with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_digestmod = "sha256"
			hfeed_h = crypto.HMAC(hfeed_digestmod, key["private"], key["feed_id"])
			hfeed_signer = crypto.HMAC(hfeed_digestmod, bytes.fromhex(hfeed_h.get_private_key()))
	
	with open(vfeed_key_path, 'rb') as f:
			vfeed_privKey = f.read()
			vfeed_h = crypto.HMAC(hfeed_digestmod, vfeed_privKey, vfeed_name)
			vfeed_signer = crypto.HMAC(hfeed_digestmod, vfeed_privKey)
	
	#shortpath file to get the sequence and the hash of the previous event, so we don't have to search all the hostfeeds till the end first
	with open(vfeed_stats_path, 'r') as f:
			key = eval(f.read())
			vfeed_seq = key["vfeed_seq"]
			vfeed_hprev = key["vfeed_hprev"]
			vfeed_sig = key["vfeed_sig"]

	if verifySign(vfeed_privKey,vfeed_sig,[vfeed_seq,vfeed_hprev]):
		hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
		
		e = event.EVENT(fid=vfeed_h.get_feed_id(), seq=vfeed_seq,
						hprev=vfeed_hprev, content=message,
						digestmod=hfeed_digestmod)
		metabits = e.mk_metabits(vfeed_signer.get_sinfo())
		signature = vfeed_signer.sign(metabits)
		w = e.to_wire(signature)
		#print("w:",w)
		hfeed.write(w)
		updateStats(vfeed_name, message)


def sign(vfeed_privKey,data):
	hash = hashlib.sha256(vfeed_privKey).hexdigest()
	for i in data:
		hash = hash + hashlib.sha256(bytes(i, "utf-8")).hexdigest()
		hash = hashlib.sha256(bytes(hash, "utf-8")).hexdigest()
	print("signature: ",hash)
	return hash

def verifySign(vfeed_privKey,vfeed_sig,data):
	if(vfeed_sig == sign(vfeed_privKey, data)):
		print("signature valid")
		return True
	else:
		print("signature invalid")
		return False
	
#TODO:	reading in pubkey from
def get_hfeed(hfeed_name):
	hfeed_pcap_path = "data/"+hfeed_name+"-feed.pcap"
	hfeed_key_path =  "data/"+hfeed_name+"-secret.key"
	hfeed_digestmod = "sha256"
	hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)

def getContent(hfeed):
	for event in hfeed: 
		print("Feedcontent: ", event.content())


def test():
	
	vfeed_name = createVirtualFeed()
	getvfeed_privKey(vfeed_name)
	createEvent("Alice",vfeed_name,"Hello world!")
	createEvent("Alice",vfeed_name,"this is another example message")
	createEvent("Alice",vfeed_name,"this is the second virtual event")
	

test()