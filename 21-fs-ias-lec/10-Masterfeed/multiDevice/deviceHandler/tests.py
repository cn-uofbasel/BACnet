# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:10:16 2021

@author: retok
"""

import unittest, secrets, os
from uiFunctions import UiFunctions

"""
Testing class for testing the UiFunctions
"""

class TestMethods(unittest.TestCase):
    
    def __init__(self):
        self.uf = UiFunctions()
    
    def generate_test_keys(self):
        self.path = os.getcwd()
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
            self.assertTrue(pkWork == pkOriginal)
        



"""
Entry point when running from console or other modules together
with main- Method called on execution
"""
def main():
    tm = TestMethods()
    
    # test keys equal after en- and decryption
    tm.generate_test_keys()
    #tm.test_key_equals(pw = 'Hello')
    
if __name__ == "__main__":
    main()
    
        
    
    # # test password and verification'
    # kdf = uf.key_derivation_function()       
    # key = uf.generate_key_from_pw(pw)    
    # kdf.verify(pw.encode(), key)