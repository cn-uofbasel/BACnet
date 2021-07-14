#!/usr/bin/env python3

import sys
# add the lib to the module folder
sys.path.append("./lib") 


import os
import crypto 
import feed 
import hashlib

def makeFiles():
	if not os.path.isdir("data"): 
		print("creating directories:\ndata\ndata/virtual")
		os.mkdir("data")
		os.mkdir("data/virtual")

	
def getLastMsg():
	print("gets the last message of the virtual feed")

def getvfeed_privKey(vfeed_name):
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_path, 'r') as f:
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
	with open(vfeed_path, "w") as f: 
		f.write(key["private"])
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
			vfeed_seq = key["sequence"]+1
			vfeed_hprev = key["hprev"]
			vfeed_sig = key["vfeed_sig"]
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey(vfeed_name)
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

def createFeed():
	print("creates new virtual Feed")

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
	
	with open(vfeed_key_path, 'r') as f:
			key = eval(f.read())
			vfeed_digestmod = key["type"][5::]
			vfeed_h = crypto.HMAC(vfeed_digestmod, key["private"], key["feed_id"])
			vfeed_signer = crypto.HMAC(vfeed_digestmod, bytes.fromhex(vfeed_h.get_private_key()))
	
	
	#shortpath file to get the sequence and the hash of the previous event, so we don't have to search all the hostfeeds till the end first
	with open(vfeed_stat_path, 'r') as f:
			key = eval(f.read())
			vfeed_seq = key["sequence"]
			vfeed_hprev = key["hprev"]
			vfeed_sig = key["vfeed_sig"]
	
	hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
	
	
	print("creates a new event:")

def sign(vfeed_privKey,data):
	hash = hashlib.sha256(bytes(vfeed_privKey, "utf-8")).hexdigest()
	for i in data:
		hash = hash + hashlib.sha256(bytes(i, "utf-8")).hexdigest()
		hash = hashlib.sha256(bytes(hash, "utf-8")).hexdigest()
	print("signature: ",hash)
	return hash

def test():
	vfeed_name = createVirtualKeypair()
	makeFiles()
	createStats(vfeed_name, "0", "0")
	#getHostFeeds(vfeed_name)
	getvfeed_privKey(vfeed_name)
	

test()