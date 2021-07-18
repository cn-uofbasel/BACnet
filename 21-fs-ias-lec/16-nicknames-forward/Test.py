import sys
import pickle


def main():

    """
    # creat connectedPerson.pkl file
    dictionary2 = {}
    file = open("connectedPerson.pkl", "wb")
    pickle.dump(dictionary2, file)
    file.close()

    """

    if sys.argv[1] == 'Nickname':
        changeName(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == 'Username':
        changeUsername(sys.argv[2], sys.argv[3])

    else:
        newName = sys.argv[1]

        username_file = open("username.pkl", 'rb')
        username_dict = pickle.load(username_file)
        username_file.close()

        if not newName == username_dict['username']:
            file = open('connectedPerson.pkl', 'rb')
            connPep = pickle.load(file)
            file.close()

            alreadyExists = False

            for entry in connPep:
                if entry == newName:
                    alreadyExists = True
                    break

            if not alreadyExists:
                connPep[newName] = newName
                file = open('connectedPerson.pkl', 'wb')
                pickle.dump(connPep, file)
                file.close()

        print(connPep)


def changeName(oldName, newName):

    with open('connectedPerson.pkl', 'rb') as f:
        file = pickle.load(f)
    f.close()

    key = ''
    items = file.items()
    for t in items:
        if t[1] == oldName:
            key = t[0]

    file[key] = newName

    f = open('connectedPerson.pkl', 'wb')
    pickle.dump(file, f)
    f.close()

    print(file)

def changeUsername(oldName, newName):

    username_file = open("username.pkl", 'rb')
    username_dict = pickle.load(username_file)
    username_file.close()

    if not oldName == username_dict['username']:

        f = open('connectedPerson.pkl', 'rb')
        entries = pickle.load(f)
        f.close()

        for entry in entries:
            # entry[0] = key for specific entry, content[1]['fromUser'] = oldUsername
            if entry == oldName:
                print("entry found")
                # there is no nickname for this person
                if entry == entries[entry]:
                    print("no nickname")
                    entries[newName] = newName
                    entries.pop(entry)
                    break
                else:
                    print("with nickname")
                    # there is a nickname for this person
                    entries[newName] = entries[oldName]
                    entries.pop(entry)
                    break

    f = open('connectedPerson.pkl', 'wb')
    pickle.dump(entries, f)
    f.close()
    print(entries)


if __name__ == '__main__':
    main()
