#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 15:15:14 2020

@author: yannickrummele
"""

#from uiFunctionsHandler import UiFunctionHandler
from .uiFunctionsHandler import *


ufh = UiFunctionHandler()

def update_feedIds():
    print("update feedIDs")
    feedIDsTree.delete(*feedIDsTree.get_children())
    allMasterIDs = list(ufh.get_master_ids())

    for i in range(len(allMasterIDs)):
        treeUsername=ufh.get_username(allMasterIDs[i])
        treeID=allMasterIDs[i].hex()
        feedIDsTree.insert('', 'end', treeUsername, text=treeUsername, values=treeID)
        feedIDsTree.item(treeUsername, tags = ('master'))


        feedIDs=ufh.get_all_master_ids_feed_ids(allMasterIDs[i])

        trusted = list(ufh.get_trusted())
        blocked = list(ufh.get_blocked())
        for feedID in feedIDs:

            if feedID in trusted:
                treeApplicationName = ufh.get_application(feedID)
                treeApplicationID = feedID.hex()
                if treeApplicationName is not None:
                    followedChildname = treeUsername + " followed " + treeApplicationName
                    feedIDsTree.insert(treeUsername, 'end', followedChildname, text=treeApplicationName,
                                       values=treeApplicationID)
                    feedIDsTree.item(followedChildname, tags=('followed'))
            elif feedID in blocked:
                treeApplicationName = ufh.get_application(feedID)
                treeApplicationID = feedID.hex()
                if treeApplicationName is not None:
                    blockedChildname = treeUsername + " blocked " + treeApplicationName
                    feedIDsTree.insert(treeUsername, 'end', blockedChildname, text=treeApplicationName,
                                       values=treeApplicationID)
                    feedIDsTree.item(blockedChildname, tags=('blocked'))
            else:
                treeApplicationName = ufh.get_application(feedID)
                treeApplicationID = feedID.hex()
                if treeApplicationName is not None:
                    blockedChildname = treeUsername + " blocked " + treeApplicationName
                    feedIDsTree.insert(treeUsername, 'end', blockedChildname, text=treeApplicationName,
                                       values=treeApplicationID)
                    feedIDsTree.item(blockedChildname)

def setTrusted():
    feedIDsTree.bind('<<TreeviewSelect>>', callback)
    print("trusted")
    curItemID = (feedIDsTree.selection()[0])
    curItem="".join(feedIDsTree.item(feedIDsTree.selection()[0])['values'])
    curID=bytes.fromhex(curItem)
    print(curItem)
    print(curID)
    ufh.set_trusted(curID, True)
    feedIDsTree.item(curItemID, tags=('followed'))

def setUntrusted():
    feedIDsTree.bind('<<TreeviewSelect>>', callback)
    print("untrusted")
    curItemID= (feedIDsTree.selection()[0])
    curItem = "".join(feedIDsTree.item(feedIDsTree.selection()[0])['values'])
    curID = bytes.fromhex(curItem)
    print(curItem)
    print(curID)
    ufh.set_trusted(curID, False)
    feedIDsTree.item(curItemID, tags=('blocked'))


def callback(event):
    print(feedIDsTree.selection()[0])

def updateUsername():
    ufh.set_username(entryUsername.get())
    print("New username: " + entryUsername.get())
    #entryUsername.delete(0,END)

def updateRadius():
    try:
        radius=int(entryRadius.get())
        ufh.set_radius(radius)
        print("New radius: "+ entryRadius.get())

    except Exception as e:
        print("Insert a integer for the radius")
        print(e)
        print(entryRadius.get() + " is not a integer")


#generate_test_data()


def run():

    try:
        root.mainloop()
        root.destroy()
        root.close()
        exit()
    except:
        pass
