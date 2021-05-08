
import json

def main(blocklistpath):

    file = open(blocklistpath, "r")

    blocklist = json.load(file)
    print(blocklist["words"])



main("./myblocklist.json")