#version 15:38
import random
import string
#name = 'zzz'
set_off = 23

def convert(name):
    
    for i in range(len(name)):
        if name[i].lower() == 'i' or name[i].lower() == 'y' or name[i].lower() == '9':
            name = list(name)
            name[i] = 'g'
            name = ''.join(name)
    
    indx = 0
    c=0
    while len(name) < 6:
        if c >16:
            return '#ffb300'  # just in case it goes into an infinate Loop (probability is very, very low)
        c +=1
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
    
def name_to_color(name):
    color = convert(name)
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    if r<128 or g<128 or b<128 and len(name) == 7:
        return color
    else:
        return '#00f7ff'  # some ord() chars aren't convertable. When we checked all, we found this to be the case with i, y and 9 which is why we prevent the program from outputting them. Just in case there are any other letters that we forgot to check, we added this clause. Should never get here but the presentation got us worried cuase if the color is not exactly 6 digits long, tkinter crashes.
  
