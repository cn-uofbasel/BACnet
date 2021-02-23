from browser import create,  inputhandler_old
from net import client_old
import os


def clear():
    try:
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
    except:
        None

if __name__ == "__main__":
    exit_flag = False
    while True:
        clear()
        if exit_flag:
            break
        print(create.logo())
        print(create.welcome())
        session_client = client_old.Client()

        while True:
            try:
                connec = session_client.get_connection()
                if connec:
                    if connec == "quit":
                        exit_flag = True
                    break
            except KeyboardInterrupt:
                print(create.thank())
                exit()
        if exit_flag:
            break

        session_inputhandler = inputhandler_old.InputHandler(session_client)

        while True:
            try:
                result = session_inputhandler.get_input()
                if result == "quit":
                    session_client.server_socket.close()
                    break
            except KeyboardInterrupt:
                session_client.server_socket.close()
                print(create.thank())
                exit()
            except:
                session_client.server_socket.close()
                break
    print(create.thank())


