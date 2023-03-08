from argparse import ArgumentParser

from xbutils.cmd import Cmd, Param

Cmd.version = 'cmd example v1.0.0'

# ==============================
# cmd1 : as class with function
# ===============================
def cmd1():
    print("Run cmd1")


class Cmd1(Cmd):
    name = 'cmd1'
    function = cmd1
    help = "cmd1 help"
    desc = "cmd1 desc"


# ==================================
# cmd2 : as class with function name
# and parameter
# =================================

def cmd2(param: str):
    print("Run cmd2 with param=", param)


class Cmd2(Cmd):
    name = ('cmd2', 'c2')
    function = "cmd.cmd2"
    help = "cmd2 help"
    desc = "cmd2 desc"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--param', "-P")


# ===================
# cmd3 : as instance
# ===================


def cmd3(**params):
    print("Run cmd2 with params=", params)


Cmd(name='cmd3', function=cmd3, params=[Param('--param1', '-1'), Param("--param2", '-2', type=int)])


# ===================
# cmd4 : as decorator
# ===================

@Cmd(name="cmd4")
def cmd4():
    print("Run cmd4")

if __name__ == '__main__':
    Cmd.main()
