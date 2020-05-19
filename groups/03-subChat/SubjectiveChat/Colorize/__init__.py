#version 15:38
import random
import string
#name = 'bill'
set_off = 23

def name_to_color(name):
    
    for i in range(len(name)):
        if name[i].lower() == 'i' or name[i].lower() == 'y' or name[i].lower() == '9':
            name = list(name)
            name[i] = 'g'
            name = ''.join(name)
    
    indx = 0
    while len(name) < 6:
        new_letter = chr(65 + (ord(name[indx]) + set_off + (indx*6) )%25) # this keeps the char within the range of A-Z in the asci table and adds variation in case the letter is the same (indx*6)
        if new_letter.lower() != 'i' and new_letter.lower() != 'y' and new_letter != '9':
            name = name + new_letter #add the letter
            indx = (indx+1)%len(name)
        
    if len(name) > 6:
        name = name[:6] #cut name if too long
        
    name = list(name) # make it a list so we can edit it more easily
    
    for i in range(len(name)):
        Integer = (ord(name[i])+set_off)%16
        Hex = Integer.to_bytes(((Integer.bit_length() + 7) // 8),"big").hex()
        #print("...."+Hex)
        Hex = Hex[1:]
        name[i] = Hex  
            
    name = ''.join(name)
    color = '#' + name
    return color
