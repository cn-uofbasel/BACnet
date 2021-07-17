#!/usr/bin/env python3

import sys
# add the lib to the module folder
sys.path.append("./lib") 

#some code is used from lib/event, lib/feed, and demo.py(from BACnet) to implement some parts of this program.

import os
import crypto 
import feed 
import event
import hashlib
import json

#*** Supported Methods *******************
#
#--- divers Methods ----------------------
#
# - makeFiles()
# - isOldName(name)
# - get_vEvent_from_Wire(w)
# - getChronologicVFeedContent()
#
#--- Stats operations Methods ------------
#
# - createStats(vfeed_name,vfeed_seq,vfeed_hprev)
# - updateStats(vfeed_name,content)
# - getStats()
# - sign(vfeed_privKey,data)
# - verifySign(vfeed_privKey,vfeed_sig,data)
#
#--- hfeed Methods -----------------------
#
# - getHostFeeds()
# - gethfeed_pubKey(hfeed_name)
# - gethfeed_privKey(hfeed_name)
# - getLocalhfeedName()
# - get_hfeed(hfeed_name)
# - gethFeedContent(hfeed)
# - createHostKeypair()
#
#--- vfeed Methods -----------------------
#
# - getvfeed_name()
# - getvfeed_privKey()
# - createVirtualFeed()
# - createVirtualEvent(message)
# - createVirtualKeypair()
# - getvFeedContent(hfeed)
# 
#******************************************
#TODO: vfeed_name oder vfeed_id? vereinheitlichen!
#TODO: Methode zum einlesen von Hostfeeds im devices.json
#TODO: Code beschriften
#TODO: main/demo zum text schreiben & lesen

def makeFiles():
	if not os.path.isdir("data"): 
		print("please run deviceHandler.py first")
		#pcap_path = "data/"+getLocalhfeedName()+".pcap"
	#if not os.path.isfile(pcap_path):
		
	
def getLastMsg():
	print("lastFeedcontent: ", event.content())
	print("gets the last message of the virtual feed")


def getvfeed_name():
	file = [f for f in os.listdir("data/virtual") if f.endswith('.key')]
	if file == []:
		print("please create a keypair first")
		vfeed_name = -1
	else:
		vfeed_name = file[0].split('.key')[0]
		#print("vfeed_name",vfeed_name)	
	return (vfeed_name)

#Determines if name is in old (read in keys like: alice-secret.key) or in the new (read in keys like: lskdhfiuew234g35.key) format
#-> backwardscompatibility
def isOldName(name):
	if(name == -1):
		print("Error: in isOldName")
		return False
	else:
		test1 = len(name)==16
		test2 = name.isalnum()
		test3 = name.islower()
	if(test1 & test2 & test3):
		return False
	else:
		return True

def gethfeed_pubKey(hfeed_name):
	if (isOldName(hfeed_name)):
		hfeed_key_path =  "data/"+hfeed_name+"-secret.key"
		with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_pupKey = key["feed_id"]
		return hfeed_pupKey
	else:
		return hfeed_name
	

def gethfeed_privKey(hfeed_name):
	if (isOldName(hfeed_name)):
		hfeed_key_path =  "data/"+hfeed_name+"-secret.key"
		with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_privKey = key["private"]
	else:
		hfeed_key_path =  "data/"+hfeed_name+".key"
		with open(hfeed_key_path, 'rb') as f:
				hfeed_privKey = f.read()
	return hfeed_privKey

def getvfeed_privKey():
	vfeed_name = getvfeed_name()
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_path, 'rb') as f:
			vfeed_privKey = f.read()
	print("private key: ",vfeed_privKey)
	return vfeed_privKey

def createVirtualKeypair():
	vfeed_name = getvfeed_name()
	if (vfeed_name == -1):
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
		print("Creating new virtual Feed Keypair")
		return vfeed_id
	else:
		print("A virtual Feed Keypair already exists.")
		return vfeed_name
	
def createHostKeypair():
	print("createHostKeypair()")
	hfeed_name = getLocalhfeedName()
	if (hfeed_name == -1):
		hfeed_digestmod = "sha256"
		hfeed_h = crypto.HMAC(hfeed_digestmod)
		hfeed_h.create()
		di = '{\n  '+(',\n '.join(hfeed_h.as_string().split(','))[1:-1])+"\n}"
		key = eval(di)
		hfeed_id = key["feed_id"]
		print("hfeed_name:",key["feed_id"])
		hfeed_path = "data/" + hfeed_id + ".key"
		print("Create host key pair at",hfeed_path) 
		print("write key: ",key["private"])
		with open(hfeed_path, "wb") as f: 
			f.write(hfeed_h.get_private_key())
		return hfeed_id
	else:
		print("A host Feed Keypair already exists.")
		return hfeed_name

def createStats(vfeed_name,vfeed_seq,vfeed_hprev):
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	vfeed_key_path = "data/virtual/" + vfeed_name + ".key"
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey()
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
	vfeed_privKey = getvfeed_privKey()
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

def getStats():
	vfeed_name = getvfeed_name()
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	with open(vfeed_stats_path, 'r') as f:
			key = eval(f.read())
			vfeed_seq = key["vfeed_seq"]
			vfeed_hprev = key["vfeed_hprev"]
			vfeed_sig = key["vfeed_sig"]
	return [vfeed_seq,vfeed_hprev,vfeed_sig]

def createVirtualFeed():
	print("Creating new virtual Feed...")
	vfeed_name = createVirtualKeypair()
	createStats(vfeed_name, "0", "None")
	return vfeed_name

def createVirtualEvent(message):
	# hfeed is the host feed of the virtual feed (vfeed)
	# mode: mode to operate files: 0 = old way (read in keys like: alice-secret.key), 1 = new way (read in keys like: lskdhfiuew234g35.key)
	hfeed_name = getLocalhfeedName()
	if(hfeed_name == -1):
		print("Please open UI.py first!")
		sys.exit(-1)
	vfeed_name = getvfeed_name()
	if (isOldName(hfeed_name)):
		hfeed_key_path =  "data/"+hfeed_name+"-secret.key"
	else:
		hfeed_key_path =  "data/"+hfeed_name+".key"
		
	hfeed_pcap_path = "data/"+hfeed_name+"-feed.pcap"
	vfeed_key_path =  "data/virtual/" + vfeed_name + ".key"
	vfeed_stats_path = "data/virtual/" + vfeed_name + ".stats"
	hfeed_digestmod = "sha256"
	#host_feed read out
	
	if(isOldName(hfeed_name)):
		with open(hfeed_key_path, 'r') as f:
				key = eval(f.read())
				hfeed_h = crypto.HMAC(hfeed_digestmod, key["private"], key["feed_id"])
				hfeed_signer = crypto.HMAC(hfeed_digestmod, bytes.fromhex(hfeed_h.get_private_key()))
	else:
		with open(hfeed_key_path, 'rb') as f:
				hfeed_h = crypto.HMAC(hfeed_digestmod, f.read(), hfeed_name)
				hfeed_signer = crypto.HMAC(hfeed_digestmod, f.read())
		
	
	with open(vfeed_key_path, 'rb') as f:
			vfeed_privKey = f.read()
			vfeed_h = crypto.HMAC(hfeed_digestmod, vfeed_privKey, vfeed_name)
			vfeed_signer = crypto.HMAC(hfeed_digestmod, vfeed_privKey)
	
	#shortpath file to get the sequence and the hash of the previous event, so we don't have to search all the hostfeeds till the end first
	stats = getStats()
	vfeed_seq = stats[0]
	vfeed_hprev = stats[1]
	vfeed_sig = stats[2]

	if verifySign(vfeed_privKey,vfeed_sig,[vfeed_seq,vfeed_hprev]):
		hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
		
		e = event.EVENT(fid=vfeed_h.get_feed_id(), seq=vfeed_seq,
						hprev=vfeed_hprev, content=">"+ message,
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

def getLocalhfeedName():
	file = [f for f in os.listdir("data") if f.endswith('.key')]
	localhfeed_name =  -1
	if file == []:
		print("Error 404: No hostkey found")
	else:
		localhfeed_name = file[0].split('.key')[0]
		if localhfeed_name.endswith('-secret'):
			localhfeed_name = localhfeed_name.split('-secret')[0]
	return (localhfeed_name)

def get_hfeed(hfeed_name):
	hfeed_digestmod = "sha256"
	hfeed_pcap_path =  "data/"+hfeed_name+"-feed.pcap"
	hfeed_h = crypto.HMAC(hfeed_digestmod, gethfeed_privKey(hfeed_name), gethfeed_pubKey(hfeed_name))
	hfeed_signer = crypto.HMAC(hfeed_digestmod, gethfeed_privKey(hfeed_name))
	hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
	return hfeed

def getHostFeeds():
	devicesPath = "data/virtual/devices.json"
	hostFeedArray = []
	with open(devicesPath, 'r') as f:
		data = json.load(f)
	for i in data:
		hostFeedArray.append(i)
		#print(hostFeedArray)
	return hostFeedArray

def gethFeedContent(hfeed):
	for event in hfeed: 
		print("hFeedcontent: ", event.content())
		
		
def getvFeedContent(hfeed):
	msgArr = []
	for event in hfeed: 
		vevent = get_vEvent_from_Wire(event.content())
		message = vevent.content().decode("utf-8")
		message = message.split(">",1)
		if(len(message)==2):
			msgArr.append(message[1])
		else:
			msgArr.append(message)
	return msgArr

def getvFeedSeq(hfeed):
	seqArr = []
	for event in hfeed: 
		vevent = get_vEvent_from_Wire(event.content())
		seqNr = vevent.seq
		seqArr.append(seqNr)
	return seqArr

def get_vEvent_from_Wire(w):
		wire = w
		e = event.deserialize(w)
		metabits, signature = e[:2]
		contbits = None if len(e) < 2 else e[2]
		fid, seq, hprev, sinfo, hcont = \
		event.deserialize(metabits)[:5]
		hval = hprev[1] if hprev != None else hcont[1]
		dm = 'sha256'
		ve = event.EVENT(fid=fid, seq=seq,
						hprev=hprev, content=contbits,
						digestmod=dm)
		return ve

def getChronologicVFeedContent():
	hFeedNamearray = getHostFeeds()
	hFeedArray = []
	msgArray = []
	seqArray = []
	for i in hFeedNamearray:
		hFeedArray.append(get_hfeed(i))	
	print("hFeedArray:",hFeedArray)
	for feed in hFeedArray:
		msgArray = msgArray + getvFeedContent(feed)
		seqArray = seqArray + getvFeedSeq(feed)
	print("msgArray: ",msgArray)
	print("seqArray: ",seqArray)
	for j in range(0,len(seqArray),1):
		for k in range(0,len(seqArray),1):
			if int(seqArray[k]) == j:
				print(msgArray[k])
			
			

def test():

	#createHostKeypair()
	#createVirtualFeed()
	#getvfeed_privKey()
	#vfeed_name = getvfeed_name()
	createVirtualEvent("Hello world!")
	createVirtualEvent("this is another example message")
	createVirtualEvent("this is the second virtual event")
	print("getLocalhfeedName: " ,getLocalhfeedName())
	#print("hfeed: ",get_hfeed(getLocalhfeedName()))
	#print(getvFeedContent(get_hfeed(getLocalhfeedName())))
	#print(gethFeedContent(get_hfeed(getLocalhfeedName())))
	getHostFeeds()
	getChronologicVFeedContent()
test()