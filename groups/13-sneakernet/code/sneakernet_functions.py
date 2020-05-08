from .logMerge import *
import os

logM = LogMerge()
def importing():
    ### TO DO ### insert logMerge getPath() logic
    path = ['']
    try:
        if path == '':
            path = input("Insert your path to pcap file EX: F://BACNet/")
            logM.import_logs(path)
        else:
            logM.import_logs(path)
    except FileNotFoundError:
        print("File not found, something went wrong")


def exporting():
    ### TO DO ### insert logMerge getPath() logic
    amount = input("How many messages would you like to export?")
    try:
        amount = int(amount)
    except ValueError:
        print("ups")
        return
    path = ''
    if path == '':
        path = input("Insert your path to pcap file EX: F://BACNet/")

    logM.export_logs(path, getSequenceNumbers(), amount)


def getPath():
    ### TO DO ### insert automatic path logic
    pass

def viewLog():
    ### Welcher Nutzer vorhanden, wann war der letzte Export, Grösse der Dateien
    pass
def getSequenceNumbers():
    pass
def getUser():
    ### user = [(name, last login)]
    file = open('users.txt', 'r')
    users = file.read().split(' ')
    file.close()


def removeAllUsers():
    os.remove('users.txt')
    file = open('users.txt', 'w+')
    file.close()


def newUser():
    name = input("Nickname: ")
    try:
        file = open('users.txt', 'a')
        check = open('users.txt', 'r')
    except FileNotFoundError:
        file = open('users.txt', 'w+')
        check = open('users.txt', 'r')
    users = check.read().split(' ')
    if len(users) > 0:
        file.write(' ' + name)
        file.close()
        check.close()
    else:
        file.write(name)
        file.close()
        check.close()

if __name__ == '__main__':

    getUser()

