# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:10:16 2021

@author: retok
"""

import unittest, secrets, os, json
from uiFunctions import UiFunctions

"""
Testing class for testing the UiFunctions
"""

class TestMethods(unittest.TestCase):
    
    def __init__(self):
        self.uf = UiFunctions()
        self.path = os.getcwd()
    
    def generate_test_keys(self):
        self.testPath = os.path.join(os.path.dirname(os.getcwd()),'testPath')
        # generate random key files
        for x in range(5):
            private_key = secrets.token_bytes(32)
            public_key = secrets.token_bytes(32)
            with open(os.path.join(self.testPath, public_key.hex() + '.key'), 'wb') as file:
                file.write(private_key)
            # make control files for later use
            with open(os.path.join(self.testPath, 'control' ,public_key.hex() + '.key'), 'wb') as file:
                file.write(private_key)
    
    def test_key_equals(self, pw):
        # encrypte and decrypt them
        self.uf.encrypt_private_keys(pw, self.path)  
        self.uf.decrypt_private_keys(pw, self.path)  
        # check if pks
        for file in [f for f in os.listdir(self.testPath) if f.endswith('.key')]:
            f = open(os.path.join(self.testPath, file), 'rb')
            pkWork = f.read()
            f.close()
            f = open(os.path.join(self.testPath,'control', file), 'rb')
            pkOriginal = f.read()
            f.close()   
            # it seems byte equals is not yet supported in Python, thus use True with ==
            self.assertTrue(pkWork == pkOriginal, 'Keys are not equal')
            
    def test_dict2json(self):
        # create empty dictionary
        devDict = {}
        # create contents
        virtualList = []
        for i in range(5):
            virtualList.append("virtual_" + str(i))
        # add to dictionary dict[key] =  content
        key1 = secrets.token_bytes(8).hex()
        key2 = secrets.token_bytes(8).hex()
        devDict[key1] = {'deviceName': 'Alice PC', 'virtual': virtualList}
        devDict[key2] = {'deviceName': 'Alice Handy', 'virtual': virtualList}
        # get all keys as list
        devDict.keys()
        # get content at specified key, then get name of the device
        devDict.get(key1).get('deviceName')
        
        # export to JSON file
        with open(os.path.join(self.path,'devices.json'), 'w') as f:
            json.dump(devDict, f, indent=4)
        
        # import JSON file
        with open(os.path.join(self.path,'devices.json'), 'r') as f:
            dictTest = json.load(f)
        
        # check for equality
        self.assertDictEqual(devDict, dictTest, 'Dictionaries are not equal!')
        

"""
Entry point when running from console or other modules together
with main- Method called on execution
"""
def main():
    tm = TestMethods()
    
    # test keys equal after en- and decryption
    #tm.generate_test_keys()
    #tm.test_key_equals(pw = 'Hello')
    
    # test JSON Export
    tm.test_dict2json()
    
if __name__ == "__main__":
    main()
    
        
    
    # # test password and verification'
    # kdf = uf.key_derivation_function()       
    # key = uf.generate_key_from_pw(pw)    
    # kdf.verify(pw.encode(), key)