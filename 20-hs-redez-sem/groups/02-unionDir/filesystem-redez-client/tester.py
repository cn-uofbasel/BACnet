from browser import inputhandler
import os

if __name__ == "__main__":
    session_inputhandler = inputhandler.InputHandler()
    while True:
        result = session_inputhandler.get_input()
        if result == "END":
            break
