# -*- coding: utf-8 -*-
"""
Created July 2021
@author: retok
This Code needs the module crypthography. It may be necessary to install it:
    https://cryptography.io/en/latest/
    On Linux: pip3 install cryptography
"""




import math, re, os # math, reg expressions and operating system 
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # password based key derivation function
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes 

"""
Class uiFunctions providing functionality for the device handler Ui
"""
class UiFunctions:   
    
    def __init__(self):
        self.pathToKeys = 'D:\\ComputerScience\\S4\\IaS\\IV_project\\multiDevice\\testPath'
        self.dev_dict = {} 
        self.pwTestBytes = b'Ci6YPlb6MjOcMdrjl0KI' # testByteString for password verification
            
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
    def encrypt_private_keys(self, pw, path):
        # set source and target path
        source, target = self.pathToKeys, path
        files = [f for f in os.listdir(source) if f.endswith('.key')]
        if files == []:  # no files to handle, 
            raise FileNotFoundError('No files to import at specified path!')
            return
        # loop over all '.key' files in the default working dir
        for file in files:
            f = open(os.path.join(source, file), 'rb')  # read in binary mode
            pk = f.read()
            f.close()
            cipher, nonce = self.encryption(pw, pk)
            with open(os.path.join(target, file), 'wb') as f:  # writing in binary mode
                f.write(cipher)
            with open(os.path.join(target,file.split('.')[0] + '.nonce'), 'wb') as f:  # writing in binary mode
                f.write(nonce)   
       
    #method for decryption
    def decryption(self, pw, data, nonce):
        aes = self.generate_aesgcm_from_pw(pw)
        byteText = aes.decrypt(nonce, data , None)
        return byteText                                 

    # method for decrypting the private keys of feeds and writing back to files
    def decrypt_private_keys(self, pw, path):
        # set source and target path
        source, target = path, self.pathToKeys
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
            with open(os.path.join(target, file), 'wb') as f:  # writing in binary mode
                f.write(pk)  
            os.remove(os.path.join(source, file)) # delete file as its not used anymore
            os.remove(os.path.join(source,file.split('.')[0] + '.nonce'))  # delete file as its not used anymore              
                            
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



