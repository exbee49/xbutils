from typing import Union, Callable, Sequence
from argparse import ArgumentParser


class Cmd:
    _all: list["Cmd"] = list()

    #: version string
    version: str = ""

    #: ArgumentParser prog
    prog: str = None

    #: Command name
    name: Union[None, str, Sequence[str]] = None

    #: Command Function
    function: Union[str, Callable] = None

    #: Help string (in command list) hidden if None
    help = ""

    #: Help string (in commnd help)
    desc = ""

    def __init__(self) -> None:
        super().__init__()
        if isinstance(self.name, str):
            self.name = [self.name]

    def init_parser(self, subparsers):
        params = dict()
        if self.help is not None:
            params['help'] = self.help
        if self.desc:
            params['description'] = self.desc
        parser = subparsers.add_parser(self.name[0], aliases=self.name[1:], **params)
        parser.set_defaults(sub_cmd=self)
        self.add_arguments(parser)

    def add_arguments(self, parser: ArgumentParser):
        """
        Set command arguments

        Exemple::

            parser.add_argument('--value', help="Value")
        """

    def execute_cmd(self, arg):
        if isinstance(self.function, str):
            m, f = self.function.rsplit('.', 1)
            func = getattr(__import__('linux_admin_utils.' + m, globals(), locals(), [f]), f)
        else:
            func = self.function

        func(**vars(arg))

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if cls.name is not None:
            cls._all.append(cls())

    @classmethod
    def main(cls):
        parser = ArgumentParser(prog=cls.prog)
        if cls.version:
            parser.add_argument('--version', "-V", action='version', version=cls.version)
        parser.set_defaults(subcmd=None)
        subparsers = parser.add_subparsers(metavar="", help='', title="Commands")
        for i in Cmd._all:
            i.init_parser(subparsers)
        arg = parser.parse_args()
        if not arg.subcmd:
            parser.print_help()
            return
        arg.sub_cmd.execute_cmd(arg)
