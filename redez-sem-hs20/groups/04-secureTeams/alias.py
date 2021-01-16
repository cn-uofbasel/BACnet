from json import dump, load

def addAlias(alias: str, id: str) -> bool:
    try:
        with open("alias.txt", "r") as f:
            a = load(f)
    except:
        a = []
    if a.__contains__(alias):
        print("alias already in use, choose something other than", alias)
    try:
        with open("alias.txt", "w") as f:
            a.append([alias,id])
            dump(a,f)
            return True
    except:
        return False

def getAliasById(id: str) -> str:
    try:
        with open("alias.txt", "r") as f:
            for a in load(f):
                if a[1]==id:
                    return a[0]
            return None
    except:
        return id[:6]

def getIdByAlias(alias: str) -> str:
    try:
        with open("alias.txt", "r") as f:
            for a in load(f):
                if a[0]==alias:
                    return a[1]
            return None
    except:
        return None
