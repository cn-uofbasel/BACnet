from browser import help

class Protocol:

    def __init__(self, unionpath):
        self.unionpath = unionpath
        self.client = self.unionpath.client

    def send_connection_info(self):
        hash = self.unionpath.user_hash
        name = self.unionpath.user_name
        self.client.send("CON {} {}".format(hash, name))

    def handle(self, cmds):
        if not self.unionpath.connected:
            return

        # prevent KeyError when enter is pressed
        if len(cmds) == 0:
            return

        # [reg, register]
        elif help.check_if_alias(cmds[0], 'reg'):
            return self.send_connection_info()

        # [con, conn, connect]
        elif help.check_if_alias(cmds[0], 'con'):#TODO
            return self.send_connection_info()

        # [cd, chdir]
        elif help.check_if_alias(cmds[0], 'cd'):
            return self.operator.cd(cmds)

        # [open, op]
        elif help.check_if_alias(cmds[0], 'open'):
            self.operator.open(cmds)

        # [ls, readdir, list, l]
        elif help.check_if_alias(cmds[0], 'ls'):
            self.operator.ls(cmds)

        # [srv, srvls, serverlist]
        elif help.check_if_alias(cmds[0], 'srv'): #TODO
            self.operator.srv(cmds)

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            self.operator.mk(cmds)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            self.operator.add(cmds)

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            self.operator.rm(cmds)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mt'): #TODO
            self.operator.mount(cmds)

        # [mv, move]
        elif help.check_if_alias(cmds[0], 'mv'):
            self.operator.mv(cmds)

        # [cp, copy]
        elif help.check_if_alias(cmds[0], 'cp'):
            self.operator.cp(cmds)

        # [rn, rename]
        elif help.check_if_alias(cmds[0], 'rn'):
            self.operator.rn(cmds)

        # [f, find, locate, search]
        elif help.check_if_alias(cmds[0], 'f'): #TODO
            self.operator.rn(cmds)

        # [--help, -help, help, hlp, -h, h]
        elif help.check_if_alias(cmds[0], '--help'):
            self.operator.hlp(cmds)

        # [q,-q,quit]
        elif help.check_if_alias(cmds[0], 'quit'):
            return self.operator.quit(cmds)

        # [clear, clc, clean]
        elif help.check_if_alias(cmds[0], 'clear'):
            self.operator.clear(cmds)

        # [unknown]
        else:
            self.operator.unknown(cmds)

