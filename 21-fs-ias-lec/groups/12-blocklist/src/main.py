
from blocklist import Blocklist
from blocksettings import Blocksettings

def main(blocklistpath):
    b = Blocklist(blocklistpath)
    print(b.getBlocklist())
    b.blockWord("test")
    print(b.getBlocklist())
    b.unblockWord("test")
    b.writeToFile("./myblocklist.json")
    print(b.getBlocklist())

    bs = Blocksettings.getStandartSettings()
    bs.valuesToJson()
    bs.writeToFile("./myblocklistsettings.json")


print("test")
main("./myblocklist.json")