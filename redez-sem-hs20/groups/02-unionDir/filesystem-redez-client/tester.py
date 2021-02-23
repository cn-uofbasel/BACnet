from browser import inputhandler

if __name__ == "__main__":
    session_inputhandler = inputhandler.InputHandler()
    print(session_inputhandler.unionpath.filesystem_root_dir)
    while True:
        result = session_inputhandler.get_input()
        if result == "quit":
            break



