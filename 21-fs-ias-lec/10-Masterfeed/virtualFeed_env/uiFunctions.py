# -*- coding: utf-8 -*-
"""
Created July 2021
@author: retok
Needs the module crypthography. It may be necessary to install it:
    https://cryptography.io/en/latest/
    pip install cryptography
"""

# math, reg expressions and operating system, json to work with .json files
# getpass to demand user name from os, sys for run time environment, shutil for copying files
import math, re, os, json, getpass, shutil
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # password based key derivation function
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes 

# add libraries to modules and import crypto
from lib import crypto

"""
Class uiFunctions providing functionality for the device handler Ui
"""
class UiFunctions:   
    
    def __init__(self):
        # here the unique host keys. they remain here
        self.pathToKeys = os.path.join(os.getcwd(),'data')
        # here are the keys, dict and stats file that are copied to another device
        self.pathToVirtual = os.path.join(os.getcwd(),'data','virtual')
        self.on_start()
        
    # method called on start of GUI
    def on_start(self):
        self.create_directories()
        # import the existing dictionary and this device id
        self.devDict = self.get_dict_from_json()
        self.thisDevId = self.get_device_Id_from_file()
        # if that does not exist, then its a new device
        if self.devDict is not None and self.thisDevId is not None:
            self.thisDevName = self.devDict.get(self.thisDevId).get('deviceName') 
        else:
            self.create_device()
            
    # create folders if not existing
    def create_directories(self):
        if not os.path.exists(self.pathToKeys):
            os.mkdir(self.pathToKeys)
        if not os.path.exists(self.pathToVirtual):
            os.mkdir(self.pathToVirtual)
        
    # method to generate devId and Name
    def create_device(self):
        # use HMAC class from crypto
        vfeed = crypto.HMAC("sha256")
        vfeed.create()
        self.thisDevId = vfeed.get_feed_id().hex()
        with open(os.path.join(self.pathToKeys,self.thisDevId + '.key'), "wb") as f: 
            f.write(vfeed.get_private_key())    		
        self.thisDevName = 'Device_' + getpass.getuser()
        # update dictionary
        self.devDict = {self.thisDevId : {'deviceName' : self.thisDevName, 'status' : 'active' }}
        self.write_dict_to_json()
                
    # method to update device name
    def update_device_name(self, name):
        self.thisDevName = name
        content = self.devDict.get(self.thisDevId)
        content.update({'deviceName': self.thisDevName})
        self.devDict.update({self.thisDevId : content}) 
        self.write_dict_to_json()
        
    # method to change device status from active to blocked
    def change_device_status(self, name):
        # there is no way to get specific content of dict by value then to loop over all keys and check each
        for key in self.devDict.keys():
            content = self.devDict.get(key)
            if content.get('deviceName') == name:
                content.update({'status': 'blocked'})
                self.devDict.update({key : content}) 
                self.write_dict_to_json()
                return
    
    # method key derivation function
    def key_derivation_function(self):
        # salt, usually random byte text for higher entropy
        # to derive the same key from the password, salt must be idencitcal, thus set fixed in method
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, # length in bytes
            salt=b'a'*64,
            iterations=100000)
        return kdf
    
    # method make cipher with AES GCM from key generated with passwort and kdf
    def generate_aesgcm_from_pw(self, pw):
        kdf = self.key_derivation_function()
        key = kdf.derive(pw.encode())        
        aes = AESGCM(key)
        return aes
    
    #  method for encryption
    def encryption(self, pw, data):
        aes = self.generate_aesgcm_from_pw(pw)
        nonce = os.urandom(16) # length in bytes
        cipher = aes.encrypt(nonce, data, None)
        return cipher, nonce

    # method for encyrpting the private keys of feeds and writing back to files
    def encrypt_private_keys(self, pw, dest, source=None):
        # set source and target path
        source = self.pathToVirtual if (source is None) else source
        files = [f for f in os.listdir(source) if f.endswith('.key')]
        if files == []:  # no files to handle, 
            raise FileNotFoundError('No Key-files to export! Start an BACnet application first.')
            return
        # loop over all '.key' files in the default working dir
        for file in files:
            f = open(os.path.join(source, file), 'rb')  # read in binary mode
            pk = f.read()
            f.close()
            cipher, nonce = self.encryption(pw, pk)
            with open(os.path.join(dest, file), 'wb') as f:  # writing in binary mode
                f.write(cipher)
            with open(os.path.join(dest,file.split('.')[0] + '.nonce'), 'wb') as f:  # writing in binary mode
                f.write(nonce)   
       
    #method for decryption
    def decryption(self, pw, data, nonce):
        aes = self.generate_aesgcm_from_pw(pw)
        byteText = aes.decrypt(nonce, data , None)
        return byteText                                 

    # method for decrypting the private keys of feeds and writing back to files
    def decrypt_private_keys(self, pw, source, dest=None):
        # set source and dest path
        dest = self.pathToVirtual if (dest is None) else dest
        files = [f for f in os.listdir(source) if f.endswith('.key')]
        if files == []:  # no files to handle, 
            raise FileNotFoundError('No files to import at specified path!')
            return
        # loop over all '.key' files in the default working dir
        for file in files:
            f = open(os.path.join(source, file), 'rb')  # read in binary mode
            cipher = f.read()
            f.close()
            f = open(os.path.join(source,file.split('.')[0] + '.nonce'), 'rb')  # read in binary mode
            nonce = f.read()
            f.close()
            pk = self.decryption(pw, cipher, nonce)
            with open(os.path.join(dest, file), 'wb') as f:  # writing in binary mode
                f.write(pk)  
        # loop to delete files, we do not start that until import was successfull
        for file in files:
            os.remove(os.path.join(source, file)) # delete file as its not used anymore
            os.remove(os.path.join(source,file.split('.')[0] + '.nonce'))  # delete file as its not used anymore              
    
    # export all other files need on new device (plain text an not encrypted)
    def export_other_files(self, dest):
        source = self.pathToVirtual
        self.write_dict_to_json()
        # export json dict file, shutil needs dest path and file name
        shutil.copyfile(os.path.join(source,'devices.json'), os.path.join(dest,'devices.json'))
        # stats file
        for file in [f for f in os.listdir(source) if f.endswith('.stats')]:
            shutil.copyfile(os.path.join(source,file), os.path.join(dest,file))

    # import all other files need on new device (plain text an not encrypted)
    def import_other_files(self, source):
        dest = self.pathToVirtual
        # load devices.json, to update device Dictionary with other devices
        tmpDict = self.get_dict_from_json(source)
        # update exiting directory with imported direcotry only if not yet in devDict
        for key in tmpDict.keys():
            if self.devDict.get(key) is None:
                self.devDict.update({key : tmpDict.get(key)})      
        # stats file
        files = [f for f in os.listdir(source) if f.endswith('.stats')]
        for file in files:
            shutil.copyfile(os.path.join(source,file), os.path.join(dest,file)) 
        # loop to delete files, we do not start that until import was successfull
        for file in files:            
            os.remove(os.path.join(source, file)) # delete file as its not used anymore
        os.remove(os.path.join(source, 'devices.json')) # delete file as its not used anymore
        self.write_dict_to_json()
    
    # method to export a dectionary to a JSON file
    def write_dict_to_json(self, dicti=None, dest=None):
        dicti = self.devDict if (dicti is None) else dicti
        dest = self.pathToVirtual if (dest is None) else dest
        with open(os.path.join(dest,'devices.json'), 'w') as f:
            json.dump(dicti, f, indent=4)
    
    # import dictionary from a JSON file
    def get_dict_from_json(self, source=None):
        source = self.pathToVirtual if (source is None) else source
        try:
            with open(os.path.join(source,'devices.json'), 'r') as f:
                dicti = json.load(f)
            return (dicti)
        except FileNotFoundError:
            return (None) # on error return None         
                        
    # import the unique Host Key (deviceID), actually name of the .key file
    def get_device_Id_from_file(self):
        file = [f for f in os.listdir(self.pathToKeys) if f.endswith('.key')]
        if file == []:
            return None
        device = file[0].split('.key')[0]
        return (device)        
        
    # method to check the password strength
    def pw_checker(self, pw):
        L = len(pw)
        R = 0        
        # check for uppercase letters
        R = R+26 if re.search(r"[A-Z]", pw) else R
        # check for lowercase letters
        R = R+26 if re.search(r"[a-z]", pw) else R
        # check for digits
        R = R+10 if re.search(r"\d", pw) else R        
        # check for spaces
        R = R+1 if re.search(" ", pw) else R       
        # check for special Unicod Characteres (assume an R of 10, in fact much larger)
        R = R+10 if re.search(r"[\u00C0-\u017E]", pw) else R  
        # check for uppercase letters
        R = R+33 if re.search(r"[`~!@#$%^&*()-=_+{}[\\\]<>|;':,./?"+r'"]', pw) else R   
        
        # calculate entropy of password 
        entropy = math.floor(L * math.log(R, 2))
        
        # determin strength from entropy following classes from https://www.pleacher.com/mp/mlessons/algebra/entropy2.html
        if (entropy < 28):
            return 'Very weak Passphrase', 'red'
        if (entropy >= 28 and entropy < 36):
            return 'Weak Passphrase', 'red'                     
        if (entropy >= 36 and entropy < 60):
            return 'Reasonable Passphrase', 'blue' 
        if (entropy >= 60 and entropy < 128):
            return 'Strong Passphrase', 'green'
        if (entropy >= 128):
            return 'Very Strong Passphrase', 'green'         



