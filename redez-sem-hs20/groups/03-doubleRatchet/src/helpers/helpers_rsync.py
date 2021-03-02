import os



path_my_directory = os.getcwd() + "/my_directory.txt"
path_other_directory = os.getcwd() + "/other_directory.txt"


def send_rsync() -> None:
    os.system(f"rsync -a --exclude='*/' --exclude='*.txt' --exclude='*.py' {get_path_my_log()} {get_path_other_log().rstrip('/')}")
    pass

def recv_rsync() -> None:
    os.system(f"rsync -a --exclude='*/' --exclude='*.txt' --exclude='*.py' {get_path_other_log()} {get_path_my_log().rstrip('/')}")
    pass

def setup() -> None:
    # Create files if they don't exist
    try:
        with open(path_my_directory, "x") as f:
            f.write(os.getcwd() + "/")
    except OSError:
        pass

    try:
        with open(path_other_directory, "x") as f:
            f.write("absolute path to log file of chat partner. for example: /home/ubuntu_user/chatapp/BACnet/redez-sem-hs20/groups/03-doubleRatchet/nonRedezDoubleRatchetDemo/")
        print("Created file for log file of partner. "
              "Please save the path to your partners log file in 'other_directory.txt'.")
        exit()
    except OSError:
        pass


def get_path_my_log() -> str:
    with open(path_my_directory, 'rt') as f:
        value = f.readline()
    return value

def get_path_other_log() -> str:
    with open(path_other_directory, 'rt') as f:
        value = f.readline()
    return value

