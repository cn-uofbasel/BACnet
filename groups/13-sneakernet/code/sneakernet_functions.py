import os
import logMerge
import Dictionary
pcapDumpPath = ""

class sneakernet_functions:

    # TODO: arguments to call functions reliably from gui
    # TODO: startup method. make this a class?

    # This should be a relative path that does not change neither during runtime and ideally nor during use
    pcapDumpPath = ""

    # This method imports events from the folder on the drive that holds the pcap files created by the export function.
    # returns nothing
    # TODO: update sequencenumbers after import -> call getCurrentUserDictionary, apply changes, call writeUserDictionary, update pcap to delete old events
    def importing(self):
        if pcapDumpPath != "":
            dictionary = logMerge.import_logs(pcapDumpPath)
        else:
            print("insert setPath() method properly here")
            pass
        Dictionary.writeUserDictionary(dictionary)
        new_dict = Dictionary.getUserDictionary()

        # does this happen here or in exporting()? i forgot
        self.update_pcap(new_dict)

    # this method calls the export_logs() function provided by group 4.
    # takes an int specifying the maximum number of events dumped per feed
    # returns nothing
    # TODO: update it to the newest version we were forced to do in a short time

    def exporting(self, maxEvents):
        logMerge.export_logs(pcapDumpPath, Dictionary.getSequenceNumbers(), maxEvents)

    # TODO: implement as follows:
    # read every feed and save its sequence number in a dictionary of {feedID:seqNo}
    # then compare it to our sequence numbers getSequenceNumbers() which is also {feedID:seqNo}
    # delete any event that has a lower seqNo than our getSequenceNumbers() returns
    # returns nothing
    def update_pcap(self, dictionary):
        pass

    # this function updates the pcapDumpPath
    # returns nothing
    def setPath(self, str):
        pcapDumpPath = str

    # this calls the as of now unimplemented function provided by group 4
    # returns a dictionary of feed_id: seq_no for the current user
    # TODO: insert group 4's method
    def getCurrentUserDictionary(self):
       pass

    # determines the maximum amount of extractable events. use get current and get abs of it with getsequencenumbers
    # returns an integer
    # TODO: implement   ...done xD
    def maxNumberofEvents(self):
        return 30


    # empties the user.txt file
    # no return
    def removeAllUsers(self):
        os.remove('users.txt')
        file = open('users.txt', 'w+')
        file.close()

    # removes one specified user identified by their username from the user.txt file
    # takes username, no return
    def removeOneUser(self, username):
        dictionary = Dictionary.getUserDictionary()
        if username in dictionary:
            print("Deleted ", username)
            del dictionary[username]
        else:
            print(username, " not found.")
        Dictionary.writeUserDictionary(dictionary)

    # add a new user to our userdictionary.
    # this function should call getCurrentUserDictionary() and writeUserDictionary()
    # takes the username of the new user and returns nothing
    # dict = {name1:dict_1,name2:dict2} where dict_1 = {feedID_1:seqNo_1}
    # TODO: Create a feed, .key file and add the user to the dictionary.. how to add them to BACNet?
    #
    def newUser(self, name):
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
