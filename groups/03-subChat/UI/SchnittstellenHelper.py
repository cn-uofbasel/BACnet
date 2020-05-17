# Stump of the returnAll interface (creates a List of example entries)
from random import randrange

dict ={
    0 : "", #Zeit
    1 : "", #Sender
    2 : "", #Empfanger
    3 : "", #Kontext
    4 : "", #Nachricht
    5 : ""  #ID
}

def returnAll():
    global List
    #for i in range(len(List)):
    #    print(List[i][3])
    return List

usernames = ["ken", "tuni", "viktor", "moritz"]
List = list()
value = ["",usernames[randrange(3)],usernames[randrange(3)],"ou yeah!"]
arrayOfDict = list()
for i in range(10):
    Dict = dict
    for j in range(4):
        dict[j] = value[j]
    dict[0] = randrange(10) # random "time"
    List.append(Dict)
    
    
def incomingMessage():
	return[1900, usernames[randrange(3)],usernames[randrange(3)],"hey, there!"]
