# -*- coding: utf-8 -*-
"""
Created July 2021
@author: retok
"""

import unittest, secrets, os
from uiFunctions import UiFunctions

"""
Testing class for testing the UiFunctions during development
Encrypting and decrypting Keys result in the same value
Exporting and Importing dict to json does not change the dict
"""
class TestMethods(unittest.TestCase):
    
    def __init__(self):
        self.uf = UiFunctions()
        self.path = os.getcwd()
    
    def generate_test_keys(self):
        self.testPath = os.path.join(os.path.dirname(os.getcwd()),'tests')
        # generate test folder
        if not os.path.exists(self.testPath):
            os.mkdir(self.testPath)
        if not os.path.exists(os.path.join(self.testPath,'control')):
            os.mkdir(os.path.join(self.testPath,'control'))
        if not os.path.exists(os.path.join(self.testPath,'decrypted')):
            os.mkdir(os.path.join(self.testPath,'decrypted'))            
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
        self.uf.encrypt_private_keys(pw, self.testPath, self.testPath)  
        self.uf.decrypt_private_keys(pw, self.testPath, os.path.join(self.testPath,'decrypted'))
        # check if pks
        for file in [f for f in os.listdir(self.testPath) if f.endswith('.key')]:
            f = open(os.path.join(self.testPath,'decrypted', file), 'rb')
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
        
        # update username
        content = devDict.get(key1)
        content.update({'deviceName': 'Alice Tablet'})
        devDict.update({key1 : content})
                
        # export to JSON file
        self.uf.write_dict_to_json(devDict, self.testPath)        
        # import JSON file
        dictTest = self.uf.get_dict_from_json(self.testPath)        
        # check for equality
        self.assertDictEqual(devDict, dictTest, 'Dictionaries are not equal!')
        

"""
Entry point when running from console or other modules together
with main- Method called on execution
"""
def main():
    tm = TestMethods()
    
    # test keys equal after en- and decryption
    tm.generate_test_keys()
    tm.test_key_equals(pw = 'Hello')
    
    # test JSON Export
    tm.test_dict2json()
    
if __name__ == "__main__":
    main()   
       
