from helper_functions.helpers import FOLDERNAME_KEYS
import os

# Running this will reset and delete all conversations.

# TODO: ask user if he is sure.
'''
input = input("Are you sure? [y/n]")
if input == 'y':
    pass
else:
    print("Abort Deletion.")
    exit()
'''

foldername = FOLDERNAME_KEYS.lstrip("/") + "/"

try:
    list = [item for item in os.listdir(os.getcwd() + FOLDERNAME_KEYS)]
    for item in list:
        os.remove(foldername + item)
    os.removedirs(foldername)
except FileNotFoundError:
    pass



foldername = "public_key/"

try:
    list = [item for item in os.listdir(os.getcwd() + "/public_key")]
    for item in list:
        os.remove(foldername + item)
    os.removedirs(foldername)
except FileNotFoundError:
    pass

try:
    os.remove("cborDatabase.sqlite")
except FileNotFoundError:
    pass

print("Deleted all conversations.")
