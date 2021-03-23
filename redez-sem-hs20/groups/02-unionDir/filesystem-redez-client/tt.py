import re

if __name__ == "__main__":
    input = input("ip: ")
    if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", input):
        print("True")
    else:
        print("False")