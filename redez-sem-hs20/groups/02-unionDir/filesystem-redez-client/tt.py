import os

def create_dirs_in_list(self, dirs, root):
    pass

if __name__ == "__main__":
    path = "/home/leonardo/.uniondir/.root/62c06520c22ec11b31683599ee31d53a9784edbf"
    files = []
    for file in os.listdir(path):
        print(file)
