import api
import argparse
import logging
import pathlib
import sys
from datetime import datetime
from cmd import Cmd


class InteractiveMode(Cmd):
    intro = 'Interactive mode: type ? to list commands.'
    prompt = '>'

    # any non path as argument to any command requiring a path will cause an error that closes the loop
    def __init__(self, myDecentFs):
        Cmd.__init__(self)
        self.myDecentFs = myDecentFs
        self.workingDirectory = '/' / myDecentFs.storage

    def do_quit(self, inp):
        """Quit the interactive mode with: 'quit', 'exit', 'q', 'x' or Ctrl-D."""
        print("quitting")
        return True

    def default(self, inp):
        if inp == 'x' or inp == 'q' or inp == 'quit' or inp == 'EOF':
            return self.do_quit(inp)
        print("Unrecognized command: {}".format(inp), "- Use '?' or 'help' to list commands.")

    def do_mkdir(self, inp):
        """Create a directory in DecentFS with: mkdir <path>"""
        try:
            self.myDecentFs.mkdir(inp)
        except api.DecentFsException as e:
            logging.error(e)

    def do_rmdir(self, inp):
        """Remove a directory path in DecentFS with: rmdir <path>"""
        try:
            self.myDecentFs.rmdir(inp)
        except api.DecentFsException as e:
            logging.error(e)

    def do_rm(self, inp):
        """Unlink path (file) in DecentFS with: rm <path>"""
        try:
            self.myDecentFs.unlink(inp)
        except api.DecentFsException as e:
            logging.error(e)

    def do_cd(self, inp):
        """Change current working directory with: cd <path>"""
        try:
            if self.myDecentFs.stat(inp)['flags'] == 'D':
                new_working_directory = pathlib.PurePosixPath(inp)
                self.workingDirectory = new_working_directory
                print(new_working_directory)
            else:
                print(inp, " is not a directory")
        except api.DecentFsFileNotFound as e:
            logging.error(e)

    def do_pwd(self, inp):
        """Print current working directory with: pwd"""
        print(self.workingDirectory)

    def do_ls(self, inp):
        """List files using glob pattern or all files in the current working directory:
         'ls [-l] <glob-pattern>' or 'ls [-l]'"""
        stats = False
        if inp.startswith('-l'):
            inp = inp[3:]
            stats = True
        if inp != "":
            try:
                if stats:
                    files = self.myDecentFs.ls(inp, details=True)
                    print('Flags:\tSize:\tTime:\tPath:')
                    for row in files:
                        date = datetime.fromtimestamp(row['timestamp']/1000000000)
                        size = _bytes_fmt(row['bytes'])
                        print('{}\t{}\t{}\t{}'.format(row['flags'], size, date.strftime('%c'), row['path']))
                else:
                    files = self.myDecentFs.ls(inp)
                    print(' '.join(sorted(files)))
            except api.DecentFsException as e:
                logging.error(e)
        else:
            try:
                if stats:
                    files = self.myDecentFs.ls(self.workingDirectory / '*', details=True)
                    print('Flags:\tSize:\tTime:\tPath:')
                    for row in files:
                        date = datetime.fromtimestamp(row['timestamp']/1000000000)
                        size = _bytes_fmt(row['bytes'])
                        print('{}\t{}\t{}\t{}'.format(row['flags'], size, date.strftime('%c'), row['path']))
                else:
                    files = self.myDecentFs.ls(self.workingDirectory / '*')
                    print(' '.join(sorted(files)))
            except api.DecentFsException as e:
                logging.error(e)

    def do_stat(self, inp): #currently mainly used for testing purposes
        """Get stat of file with: stat <path>"""
        try:
            stat = self.myDecentFs.stat(inp)
            date = datetime.fromtimestamp(stat['timestamp']/1000000000)
            size = _bytes_fmt(stat['bytes'])
            print('Path: {}\nFlags: {}\nTime: {}\nSize: {}'.format(stat['path'], stat['flags'], date.strftime('%c'), size))
        except api.DecentFsFileNotFound as e:
            logging.error(e)

    def do_cat(self, inp):
        """Show content of file with: cat <path>"""
        return self.do_get(inp)

    def do_get(self, inp):
        """Get file to read from in DecentFS with: get <path>"""
        try:
            output = open("/dev/stdout", 'wb')
            self.myDecentFs.readFile(inp, buf=output)
        except FileExistsError as e:
            logging.error(e)

    def do_put(self, inp):
        """Write to path in DecentFS: put <path>"""
        try:
            infile = open("/dev/stdin", 'rb')
            self.myDecentFs.writeFile(inp, buf=infile)
        except FileExistsError as e:
            logging.error(e)


def _main(argv) -> None:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
    parser = argparse.ArgumentParser(description='BACnet DecentFS cli', epilog='Version: ' + api.DecentFs.VERSION)
    parser.add_argument('--keyfile', help='A key generated by crypto.py', type=pathlib.Path)
    parser.add_argument('--storage', help='Use an existing DecentFS path', type=pathlib.Path)
    parser.add_argument('--opt', help='Pass custom options', type=ascii)
    parser.add_argument('--verbose', help='Verbose logging', action='store_true')
    parser.add_argument('--debug', help='Debug logging (overwrites verbose)', action='store_true')

    xorarg = parser.add_mutually_exclusive_group()
    xorarg.add_argument('--copy', help='Copy from source to target', nargs=2, type=pathlib.Path)
    xorarg.add_argument('--dump', help='Dump file system', action='store_true')
    xorarg.add_argument('--interactive', help='Enters interactive mode', action='store_true')
    xorarg.add_argument('--list', help='List files using a glob pattern', type=pathlib.Path)
    xorarg.add_argument('--mkdir', help='Create a directory in DecentFS', type=pathlib.Path)
    xorarg.add_argument('--move', help='Move from source to target', nargs=2, type=pathlib.Path)
    xorarg.add_argument('--new', help='Create new file system', action='store_true')
    xorarg.add_argument('--read', help='File to read from DecentFS', type=pathlib.Path)
    xorarg.add_argument('--remove', help='Unlink path in DecentFS', type=pathlib.Path)
    xorarg.add_argument('--rmdir', help='Remove a directory path in DecentFS', type=pathlib.Path)
    xorarg.add_argument('--stat', help='Get stat of file', type=pathlib.Path)
    xorarg.add_argument('--write', help='Write to path in DecentFS', type=pathlib.Path)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    myDecentFs = None

    if args.keyfile is None:
        logging.error('No keyfile specified')
        parser.print_help()
        sys.exit(1)

    if args.opt is None:
        opt = ''
    else:
        opt = args.opt

    try:
        myDecentFs = api.DecentFs(args.keyfile, storage=args.storage, opt=opt, createNew=args.new)
    except FileExistsError:
        logging.error('File or Directory already exists')
        sys.exit(1)

    if args.interactive:
        print('interactive')
        InteractiveMode(myDecentFs).cmdloop()

    if args.write is not None:
        try:
            infile = open("/dev/stdin", 'rb')
            myDecentFs.writeFile(args.write, buf=infile)
        except FileExistsError as e:
            logging.error(e)
            sys.exit(1)

    if args.stat is not None:
        try:
            stat = myDecentFs.stat(args.stat)
            date = datetime.fromtimestamp(stat['timestamp']/1000000000)
            size = _bytes_fmt(stat['bytes'])
            print('Path: {}\nFlags: {}\nTime: {}\nSize: {}'.format(stat['path'], stat['flags'], date.strftime('%c'), size))
            if args.verbose or args.debug:
                print('Blocks: {}'.format(stat['blocks']))
        except api.DecentFsFileNotFound as e:
            logging.error(e)
            sys.exit(1)

    if args.copy is not None:
        try:
            myDecentFs.copy(args.copy[0], args.copy[1])
        except api.DecentFsFileNotFound as e:
            logging.error(e)
            sys.exit(1)

    if args.dump:
        myDecentFs.dump()

    if args.read is not None:
        try:
            output = open("/dev/stdout", 'wb')
            myDecentFs.readFile(args.read, buf=output)
        except FileExistsError as e:
            logging.error(e)
            sys.exit(1)

    if args.move is not None:
        try:
            myDecentFs.move(args.move[0], args.move[1])
        except api.DecentFsFileNotFound as e:
            logging.error(e)
            sys.exit(1)

    if args.remove is not None:
        try:
            myDecentFs.unlink(args.remove)
        except api.DecentFsException as e:
            logging.error(e)
            sys.exit(1)

    if args.mkdir is not None:
        try:
            myDecentFs.mkdir(args.mkdir)
        except api.DecentFsException as e:
            logging.error(e)
            sys.exit(1)

    if args.rmdir is not None:
        try:
            myDecentFs.rmdir(args.rmdir)
        except api.DecentFsException as e:
            logging.error(e)
            sys.exit(1)

    if args.list is not None:
        try:
            if args.verbose or args.debug:
                files = myDecentFs.ls(args.list, details=True)
                print('Flags:\tSize:\tTime:\tPath:')
                for row in files:
                    date = datetime.fromtimestamp(row['timestamp']/1000000000)
                    size = _bytes_fmt(row['bytes'])
                    print('{}\t{}\t{}\t{}'.format(row['flags'], size, date.strftime('%c'), row['path']))
            else:
                files = myDecentFs.ls(args.list)
                print(' '.join(sorted(files)))
        except api.DecentFsException as e:
            logging.error(e)
            sys.exit(1)


def _bytes_fmt(num: int) -> str:
    """Tiny human readable file size

    https://bugs.python.org/issue31749
    https://gist.github.com/cbwar/d2dfbc19b140bd599daccbe0fe925597

    :param num: Bytes value
    :returns: Formated file size
    """
    for unit in ['', 'K', 'M']:
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, 'G')


if __name__ == '__main__':
    _main(sys.argv[1:])