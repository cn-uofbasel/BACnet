import os
import pathlib
import sys

# add the lib to the module folder
sys.path.append("../lib")

import time


class Feed:  # read from and write to the feed

    def __init__(self, id, myFeed, name):
        self.myFeed = myFeed                # Feed from lib/feed.py
        self.id = id                        # BacNetID
        self.name = name                    # Name of the feed owner
        self.timestamp = None

    def write_follow_to_feed(self, new_friends_feed):    # writes a new follow to the feed
        self.myFeed.write(["bacnet/following", time.time(), new_friends_feed.id])

    def write_unfollow_to_feed(self, ex_friends_feed):    # writes a new unfollow to the feed
        self.myFeed.write(["bacnet/unfollowing", time.time(), ex_friends_feed.id])

    def read_follow_from_feed(self):    # reads the follow list from the feed
        follow_list = []
        id_list = []

        for event in self.myFeed:
            if event.content()[0] == "bacnet/following":  # if event is a following, add follow to list
                friends_id = event.content()[2]
                if friends_id not in id_list:
                    follow_list.append({"Root": self.id, "time": event.content()[1], "Feed ID": event.content()[2]})
                    id_list.append(friends_id)
            if event.content()[0] == "bacnet/unfollowing":  # if it is an unfollowing, remove the follow from the list
                friends_id = event.content()[2]
                for entry in follow_list:
                    if entry["Feed ID"] == friends_id:
                        follow_list.remove(entry)
                        id_list.remove(friends_id)

        follow_list.sort(key=lambda msg: msg["time"])
        return follow_list

    def read_birthday_from_feed(self):    # reads the current birthday from the feed
        my_birthday = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/birthday":
                my_birthday = event.content()[2]

        return my_birthday

    def read_gender_from_feed(self):    # reads the current gender from the feed
        gender = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/gender":
                gender = event.content()[2]

        return gender

    def read_country_from_feed(self):    # reads the current country from the feed
        country = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/country":
                country = event.content()[2]

        return country

    def read_town_from_feed(self):    # reads the current town from the feed
        town = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/town":
                town = event.content()[2]

        return town

    def read_language_from_feed(self):    # reads the current language from the feed
        language = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/language":
                language = event.content()[2]

        return language

    def read_status_from_feed(self):    # reads the current status and past status from feed
        status = None
        status_list = []
        for event in self.myFeed:
            content = event.content()
            if content[0] == "bacnet/status":
                status = content[2]
                status_list = [(content[2], content[1])] + status_list
        return status, status_list

    def read_profile_pic_from_feed(self):    # reads the path of the current profile pic
        path = None
        data = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/profile_pic":
                path = event.content()[2]
        if path is None:  # return if no profile pic found
            return

        return path  # TODO profile pic - future changes; method returns two values --> , data

    # Not in use yet--------------------------------------------------------------------------------------------
    # TODO: in the future the profilepic. data also has to be shareable, this method reads it from the Feeds.
    def load_profile_pic(self, path):  # reads the current profile picture data and stores it in an image file.
        fileNameSuffix = os.path.split(path)[1]
        feedID, suffix = fileNameSuffix.split('.')
        data = None
        for event in self.myFeed:
            if event.content()[0] == "bacnet/profile_pic_data":
                data = event.content()[2]  # get data of most recent picture

        if data is not None:  # return if no profile pic data found
            picDirPath = os.path.join(pathlib.Path(os.getcwd()).parent, 'FrontEnd', 'media', 'profile_pics')
            if not os.path.exists(picDirPath):  # Check if directory already there
                os.makedirs(picDirPath)
            for file in os.listdir(picDirPath):
                if file.startswith(feedID):
                    os.remove(os.path.join(picDirPath, file))  # Delete old profile picture of this user
                    # TODO: is it more efficient to check if the file is equal?

            fullPath = os.path.join(picDirPath, feedID + '.' + suffix)
            freshImage = open(fullPath, 'wb')
            freshImage.write(data)  # write image to the defined path
            freshImage.flush()
            os.fsync(freshImage.fileno())
            freshImage.close()
    # ----------------------------------------------------------------------------------------------------------

    def write_gender_to_feed(self, gender):    # writes the new gender to the feed
        self.myFeed.write(["bacnet/gender", time.time(), gender])

    def write_birthday_to_feed(self, birthday):    # writes the new birthday to the feed
        self.myFeed.write(["bacnet/birthday", time.time(), birthday])

    def write_country_to_feed(self, country):    # writes the new country to the feed
        self.myFeed.write(["bacnet/country", time.time(), country])

    def write_town_to_feed(self, town):    # writes the new town to the feed
        self.myFeed.write(["bacnet/town", time.time(), town])

    def write_language_to_feed(self, language):    # writes the new language to the feed
        self.myFeed.write(["bacnet/language", time.time(), language])

    def write_status_to_feed(self, status):    # writes the new status to the feed
        time_var = time.time()
        self.myFeed.write(["bacnet/status", time_var, status])
        if self.timestamp is None:
            self.timestamp = time_var

    def write_influencer_to_feed(self, influencer):    # writes the influencer status to feed
        self.myFeed.write(["bacnet/influencer", time.time(), influencer])

    def write_profile_pic_to_feed(self, path, data):    # writes the new profile picture to the feed
        self.myFeed.write(["bacnet/profile_pic", time.time(), path])
        #TODO: in the future the profilepic. data also has to be shareable, this method writes it to the Feeds.
        #self.myFeed.write(["bacnet/profile_pic_data", time.time(), data])
