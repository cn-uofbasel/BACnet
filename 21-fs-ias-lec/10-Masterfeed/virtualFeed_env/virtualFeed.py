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
#--- diverse Methods ----------------------
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
# - getStatsFromfeed()
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
#--- CLI Methods ------------------------
#
# - main()
# - cliMenu(input)
# - cliHelp()
# - writeInterface()
# - readInterface()
#******************************************

#global paths
vpath = "data/virtual/"
hpath = "data/"

# Proofs if the needed file exists
# Status: Not Used, handled by Multidevice UI
def makeFiles():
	global hpath
	if not os.path.isdir(hpath): 
		print("please run UI.py first")

# returns the name/public key of the virtual feed
def getvfeed_name():
	global vpath
	file = [f for f in os.listdir(vpath) if f.endswith('.key')]
	if file == []:
		#print("please create a keypair first")
		vfeed_name = -1
	else:
		vfeed_name = file[0].split('.key')[0]
		#print("vfeed_name",vfeed_name)	
	return (vfeed_name)

# Determines if name is in old (read in keys like: alice-secret.key) or in the new (read in keys like: lskdhfiuew234g35.key) format
# -> backwardscompatibility
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

# returns the name/public key of the host feed
def gethfeed_pubKey(hfeed_name):
	global hpath
	if (isOldName(hfeed_name)):
		hfeed_key_path =  hpath+hfeed_name+"-secret.key"
		with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_name = key["feed_id"]
		return hfeed_name
	
# returns the private key of the host feed
def gethfeed_privKey(hfeed_name):
	global hpath
	if (isOldName(hfeed_name)):
		hfeed_key_path =  hpath+hfeed_name+"-secret.key"
		with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_privKey = key["private"]
	else:
		hfeed_key_path =  hpath+hfeed_name+".key"
		with open(hfeed_key_path, 'rb') as f:
				hfeed_privKey = f.read()
	return hfeed_privKey

# returns the private key of the virtual feed
def getvfeed_privKey():
	global vpath
	vfeed_name = getvfeed_name()
	vfeed_path = vpath + vfeed_name + ".key"
	with open(vfeed_path, 'rb') as f:
			vfeed_privKey = f.read()
		#print("private key: ",vfeed_privKey)
	return vfeed_privKey

# creates a virtual feed Keypair, if it doesn't already exist
def createVirtualKeypair():
	global vpath
	vfeed_name = getvfeed_name()
	if (vfeed_name == -1):
		vfeed_digestmod = "sha256"
		vfeed_h = crypto.HMAC(vfeed_digestmod)
		vfeed_h.create()
		di = '{\n  '+(',\n '.join(vfeed_h.as_string().split(','))[1:-1])+"\n}"
		key = eval(di)
		vfeed_id = key["feed_id"]
		#print("vfeed_name:",key["feed_id"])
		vfeed_path = vpath + vfeed_id + ".key"
		#print("Create virtual key pair at",vfeed_path) 
		#print("write key: ",key["private"])
		with open(vfeed_path, "wb") as f: 
			f.write(vfeed_h.get_private_key())
			#print("Creating new virtual Feed Keypair")
		return vfeed_id
	else:
		#print("A virtual Feed Keypair already exists.")
		return vfeed_name

# creates Host feed Keypair, if it doesn't already exist
# Status: Not Used, handled by Multidevice UI
def createHostKeypair():
	global hpath
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
		hfeed_path = hpath + hfeed_id + ".key"
		print("Create host key pair at",hfeed_path) 
		print("write key: ",key["private"])
		with open(hfeed_path, "wb") as f: 
			f.write(hfeed_h.get_private_key())
		return hfeed_id
	else:
		print("A host Feed Keypair already exists.")
		return hfeed_name

# makes a Statsfile with the sequence number and the hash of the last message and a Signature to prevent missuse
# the stats file is a shortcut to get the last seq and hprev without reading out the whole Feed
def createStats(vfeed_name,vfeed_seq,vfeed_hprev):
	global vpath
	vfeed_stats_path = vpath + vfeed_name + ".stats"
	vfeed_key_path = vpath + vfeed_name + ".key"
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey()
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

# updates the Statsfile
def updateStats(vfeed_name,content):
	global vpath
	vfeed_stats_path = vpath + vfeed_name + ".stats"
	vfeed_key_path = vpath + vfeed_name + ".key"
	with open(vfeed_stats_path, 'r') as f:
		key = eval(f.read())
		vfeed_seq = str(int(key["vfeed_seq"])+1)
	vfeed_hprev = hashlib.sha256(bytes(content, "utf-8")).hexdigest()
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey()
	signature = sign(vfeed_privKey, data)
	with open(vfeed_stats_path, "w") as f:
		f.write("{\n  'vfeed_seq': '"+vfeed_seq+"',\n  'vfeed_hprev': '"+vfeed_hprev+"',\n  'vfeed_sig': '"+signature+"',\n}")

# returns the sequence number, hash and the signature as array
def getStats():
	global vpath
	vfeed_name = getvfeed_name()
	vfeed_stats_path = vpath + vfeed_name + ".stats"
	#print("Statsfile: ",vfeed_stats_path)
	if os.path.isfile(vfeed_stats_path):
		with open(vfeed_stats_path, 'r') as f:
				key = eval(f.read())
				vfeed_seq = key["vfeed_seq"]
				vfeed_hprev = key["vfeed_hprev"]
				vfeed_sig = key["vfeed_sig"]
		return [vfeed_seq,vfeed_hprev,vfeed_sig]
	else:
		print("****************************************")
		print("Warnung: Stats File wurde nicht gefunden")
		print("****************************************")
		print("lese Stats aus dem Feed aus...")
		print()
		return getStatsFromfeed()

# extracts the Stats (vfeed_seq,vfeed_hprev,vfeed_sig) and returns it as array
def getStatsFromfeed():
	hFeedNamearray = getHostFeeds()
	hFeedArray = []
	msgArray = []
	seqArray = []
	for i in hFeedNamearray:
		hFeedArray.append(get_hfeed(i))	
		#print("hFeedArray:",hFeedArray)
	for feed in hFeedArray:
		seqArray = seqArray + getvFeedSeq(feed)
		msgArray = msgArray + getvFeedContent(feed)
	vfeed_seq = "0"
	x = 0
	for i in range(0,len(seqArray),1):
		if (int(seqArray[i]) > int(vfeed_seq)):
			vfeed_seq = seqArray[i]
			x = i
	vfeed_hprev = hashlib.sha256(bytes(msgArray[x], "utf-8")).hexdigest()
	data = [vfeed_seq,vfeed_hprev]
	vfeed_privKey = getvfeed_privKey()
	vfeed_sig = sign(vfeed_privKey, data)
	createStats(getvfeed_name(), vfeed_seq, vfeed_hprev)
	return [vfeed_seq,vfeed_hprev,vfeed_sig]
		
# makes a new virtual feed
# Status: Not Used
def createVirtualFeed():
	#print("Creating new virtual Feed...")
	global vpath
	vfeed_name = getvfeed_name()
	if(vfeed_name==-1):
		vfeed_name = createVirtualKeypair()
		file = [f for f in os.listdir(vpath) if f.endswith('.stats')]
		if file == []:
			createStats(vfeed_name, "0", "None")
	return vfeed_name

# makes an virtual event from the message and writes it into the Content of the host feed event (into the host feed)
def createVirtualEvent(message):
	# hfeed is the host feed of the virtual feed (vfeed)
	global hpath
	global vpath
	createVirtualFeed()
	hfeed_name = getLocalhfeedName()
	if(hfeed_name == -1):
		print("Please open UI.py first!")
		sys.exit(-1)
	vfeed_name = getvfeed_name()
	if (isOldName(hfeed_name)):
		hfeed_key_path =  hpath+hfeed_name+"-secret.key"
	else:
		hfeed_key_path =  hpath+hfeed_name+".key"
	
	#setting Paths
	hfeed_pcap_path = hpath+hfeed_name+"-feed.pcap"
	vfeed_key_path =  vpath + vfeed_name + ".key"
	vfeed_stats_path = vpath + vfeed_name + ".stats"
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
		

# returns a hash signature of the data, used for the stats file
def sign(vfeed_privKey,data):
	hash = hashlib.sha256(vfeed_privKey).hexdigest()
	for i in data:
		hash = hash + hashlib.sha256(bytes(i, "utf-8")).hexdigest()
		hash = hashlib.sha256(bytes(hash, "utf-8")).hexdigest()
		#print("signature: ",hash)
	return hash

# verifys, if the signature is valid
def verifySign(vfeed_privKey,vfeed_sig,data):
	if(vfeed_sig == sign(vfeed_privKey, data)):
		#print("signature valid")
		return True
	else:
		print("******************************************************")
		print("Warnung: Die Signatur des Statsfiles ist nicht Gültig!")
		print("   Die Message kann nicht geschrieben werden.")
		print("******************************************************")
		return False

# returns the name/public key of the local host feed
def getLocalhfeedName():
	global hpath
	file = [f for f in os.listdir(hpath) if f.endswith('.key')]
	if file == []:
		localhfeed_name =  -1
		#print("Error 404: No hostkey found")
	else:
		localhfeed_name = file[0].split('.key')[0]
		if localhfeed_name.endswith('-secret'):
			localhfeed_name = localhfeed_name.split('-secret')[0]
	return (localhfeed_name)

# returns the feed with the given name
def get_hfeed(hfeed_name):
	global hpath
	hfeed_digestmod = "sha256"
	hfeed_pcap_path =  hpath+hfeed_name+"-feed.pcap"
	hfeed_h = crypto.HMAC(hfeed_digestmod, gethfeed_privKey(hfeed_name), gethfeed_pubKey(hfeed_name))
	hfeed_signer = crypto.HMAC(hfeed_digestmod, gethfeed_privKey(hfeed_name))
	hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
	return hfeed

# returns an array of the feeds which are hosts to the virtual feed
def getHostFeeds():
	global vpath
	devicesPath = vpath + "devices.json"
	hostFeedArray = []
	if os.path.isfile(devicesPath):
		with open(devicesPath, 'r') as f:
			data = json.load(f)
		for i in data:
			hostFeedArray.append(i)
			#print(hostFeedArray)
	else:
		print("**************************************************************")
		print("Fatal: Devices File nicht gefunden! Dateisystem ev beschädigt")
		print("Die Vollständigkeit der Daten kann nicht gewährleistet werden!")
		print("**************************************************************")
		print("fahre fort mit nur dem lokalen Hostfeed...")
		print()
		hostFeedArray.append(getLocalhfeedName())
	return hostFeedArray

# returns the content of the host feed
# Status: Not Used
def gethFeedContent(hfeed):
	for event in hfeed: 
		print("hFeedcontent: ", event.content())
		
# returns the content of the virtual feed as an array of messages		
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

# returns the sequence numbers of the virtual feed contents as an array
def getvFeedSeq(hfeed):
	seqArr = []
	for event in hfeed: 
		vevent = get_vEvent_from_Wire(event.content())
		seqNr = vevent.seq
		seqArr.append(seqNr)
	return seqArr

# Here the Magic happens...
# Reads in the Binary text w and reconstructs it back to an event
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

# Some more Magic...
# reads in all the host feeds and sorts the events in order of the sequence numbers.
# Prints out the messages in a chronologic order, how they were written.
def getChronologicVFeedContent():
	hFeedNamearray = getHostFeeds()
	hFeedArray = []
	msgArray = []
	seqArray = []
	for i in hFeedNamearray:
		hFeedArray.append(get_hfeed(i))	
		#print("hFeedArray:",hFeedArray)
	for feed in hFeedArray:
		msgArray = msgArray + getvFeedContent(feed)
		seqArray = seqArray + getvFeedSeq(feed)
		#print("msgArray: ",msgArray)
		#print("seqArray: ",seqArray)
	for j in range(0,len(seqArray),1):
		for k in range(0,len(seqArray),1):
			if int(seqArray[k]) == j:
				print(msgArray[k])
				
# tests most of the functions above
# Status: Not Used, just used for developement and testing
def test():
	createHostKeypair()
	createVirtualFeed()
	getvfeed_privKey()
	vfeed_name = getvfeed_name()
	createVirtualEvent("Hello world!")
	createVirtualEvent("this is another example message")
	createVirtualEvent("this is the second virtual event")
	print("getLocalhfeedName: " ,getLocalhfeedName())
	print("hfeed: ",get_hfeed(getLocalhfeedName()))
	print(getvFeedContent(get_hfeed(getLocalhfeedName())))
	print(gethFeedContent(get_hfeed(getLocalhfeedName())))
	getHostFeeds()
	getChronologicVFeedContent()

# Command Menu of the Command Line Interface, handles the incoming commands
def cliMenu(input):
	print()
	if(input == "/write"):
		writeInterface()
	elif(input == "/read"):
		readInterface()
	elif(input == "/exit"):
		sys.exit(0)
	elif(input == "/help"):
		cliHelp()
	else:
		print("unbekannter Befehl, für Hilfe geben Sie /help ein.")

# handles the writing proces
def writeInterface():
	writing = True
	print()
	while(writing):
		msg = input("Bitte geben Sie ihre Nachricht ein:\n")
		if(msg == "/exit"):
			writing = False
		else:
			createVirtualEvent(msg)
			
# handles the readout process
def readInterface():
	print()
	print("Folgender Text wurde aus dem Virtual Feed gelesen:")
	print()
	getChronologicVFeedContent()

# displays a help text in the CLI
def cliHelp():
	print()
	print("Mögliche Befehle:                                ")
	print()
	print("/write   -> Schreiben einer Neuen Nachricht im Virtuellen Feed")
	print("/read	-> Lesen der Nachrichten im Virtuellen Feed")
	print("/exit    -> Beenden/Zurück")		
	print("/help    -> Hilfe")
	print()

# handles the start of the Program
def main():
	print("----------------------------------------------------------------------")
	print("|                                                                    |")
	print("|    Welcome to BACnet Virtual Feed and Multidevice Application      |")
	print("|                                                                    |")
	print("|  Made as Project in relation to the Lecture Internet and Security  |")
	print("|        by Prof.Dr. Christian Tschudin at University of Basel       |")
	print("|                                                                    |")
	print("|        Developer of Team 10: Masterfeed/VirtualFeed:               |")
	print("|                                                                    |")
	print("|                    - Patrick Steiner                               |")
	print("|                    - Reto Krummenacher                             |")
	print("|                    - Matthias Müller                               |")
	print("|                                                                    |")
	print("----------------------------------------------------------------------")
	if(getLocalhfeedName()==-1):
		print("			*****************************************")
		print("			Es wurde kein privater Host Key gefunden!")
		print("			!!! Bitte führen sie zuerst ui.py aus !!!")
		print("			*****************************************")
	else:
		cliHelp()
		while(True):
			cliMenu(input("\nHauptmenü:\nBitte geben sie einen Befehl ein:\n"))
		print()
		print("Auf Wiedersehen!")
	
main()