#!/usr/bin/env python3

import sys
# add the lib to the module folder
sys.path.append("./lib") 


import os
import crypto 
import feed 

def makeFiles():
	if not os.path.isdir("data"): 
		os.mkdir("data")
		os.mkdir("data/virtual")
		
	path = os.getcwd()
	path2 = os.path.dirname(os.getcwd())
	x = os.path.join(os.path.dirname(os.getcwd()),'Data')
	y = os.path.join((os.getcwd()),'Data')
	print(x)
	print(y)
	print(path)
	print(path2)

def getHostFeeds(vfeed_name):
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_path, 'r') as f:
		key = eval(f.read())
		host_feeds = key["host_feeds"].rsplit("_")
	print("gets the Feeds, the virtual Feed is embedded in:")
	print(host_feeds)
	return host_feeds
	
def getLastMsg():
	print("gets the last message of the virtual feed")

def getVkey(vfeed_name):
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	with open(vfeed_path, 'r') as f:
			key = eval(f.read())
			virtual_digestmod = key["type"][5::]
			privVkey = key["private"]
			pubVkey = key["feed_id"]
			##virtual_h = crypto.HMAC(virtual_digestmod, key["private"], key["feed_id"])
			#virtual_signer = crypto.HMAC(virtual_digestmod, bytes.fromhex(virtual_h.get_private_key()))
	print("gets the private key of the virtual feed: ")
	print("virtual digestmod: ", virtual_digestmod)
	#print("virtual_h: ", virtual_h )
	#print("virtual_signer: ",virtual_signer)
	print("private key: ",key["private"])
	print("public key: ",key["feed_id"])
	return privVkey

def createVirtualKeypair(vfeed_name):
	vfeed_path = "data/virtual/" + vfeed_name + ".key"
	vfeed_digestmod = "sha256"
	host_feeds =""
	header = ",\n  'host_feeds': '"
	
	#host_feeds = "_".join(host_feeds_array)
	host_feeds = header + host_feeds
	
	if not os.path.isfile(vfeed_path):
		print("Create virtual key pair at",vfeed_path) 
		vfeed_h = crypto.HMAC(vfeed_digestmod)
		vfeed_h.create()
		with open(vfeed_path, "w") as f: 
			f.write('{\n  '+(',\n '.join(vfeed_h.as_string().split(','))[1:-1])+"\n}")
			vfeed_signer = crypto.HMAC(vfeed_digestmod, vfeed_h.get_private_key())
	else:
		print("\033[1;33mError: File already exists \033[0m")
	

def createFeed():
	print("creates new virtual Feed")

def createEvent(hfeed_name,vfeed_name,message):
	
	# hfeed is the host feed of the virtual feed (vfeed)
	hfeed_key_path = "data/"+hfeed_name+"/"+hfeed_name+"-secret.key"
	hfeed_pcap_path = "data/"+hfeed_name+"/"+hfeed_name+"-feed.pcap"
	vfeed_key_path = "data/virtual/" + vfeed_name + ".key"
	vfeed_stat_path = "data/virtual/" + vfeed_name + ".stats"
	
	#host_feed read out
	with open(hfeed_key_path, 'r') as f:
			key = eval(f.read())
			hfeed_digestmod = key["type"][5::]
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
	
	hfeed = feed.FEED(fname=hfeed_pcap_path, fid=hfeed_h.get_feed_id(), signer=hfeed_signer, create_if_notexisting=True, digestmod=hfeed_digestmod)
	
	
	
	print("creates a new event:")

def test(vfeed_name):
	makeFiles()
	createVirtualKeypair(vfeed_name)
	getHostFeeds(vfeed_name)
	getVkey(vfeed_name)
	

test("virtualFeedA")