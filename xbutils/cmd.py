from typing import Union, Callable, Sequence
from argparse import ArgumentParser

_complete_bash_script = """
_{name}_comp() {{
    COMPREPLY=()
    if [ ${{COMP_CWORD}} -eq 1 ] ; then
        COMPREPLY=( $(compgen -W "$({cmd} complete)" -- "$2" ) )
    fi
}}
complete -F _{name}_comp  -o bashdefault -o default {cmd}
"""


class Cmd:
    _all: list["Cmd"] = list()

    #: version string
    version: str = ""

    #: ArgumentParser prog
    prog: str = None

    #: generate complete commands if True
    complete: bool = True

    #: complete words
    complete_words: list[str] = ['--help']

    #: default module name for function
    default_function_module: str = ""

    #: Command name
    name: Union[None, str, Sequence[str]] = None

    #: Command Function
    function: Union[str, Callable] = None

    #: Help string (in command list) hidden if None
    help = ""

    #: Help string (in commnd help)
    desc = ""

    #: Complete for cmd
    cmd_complete: list[str] = []

    _parser: ArgumentParser = None

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
        parser.set_defaults(sub_cmd_func=self.execute_cmd)
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
            if m[:1] == ".":
                m = self.default_function_module + m
            func = getattr(__import__(m, globals(), locals(), [f]), f)
        else:
            func = self.function

        func(**vars(arg))

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if cls.name is not None:
            cls._all.append(cls())

    @classmethod
    def complete_init(cls, subparsers):
        parser = subparsers.add_parser("complete")
        parser.set_defaults(sub_cmd_func=cls.complete_cmd)
        parser = subparsers.add_parser("complete-bash")
        parser.set_defaults(sub_cmd_func=cls.complete_bash)

    @classmethod
    def complete_cmd(cls, _):
        words = set(cls.complete_words)
        if cls.version:
            words.add('--version')
        for cmd in cls._all:
            words.add(cmd.name[0])
            for w in cmd.cmd_complete:
                words.add(w)

        print(' '.join(sorted(words)))

    @classmethod
    def complete_bash(cls, _):

        print(_complete_bash_script.format(
            cmd=cls._parser.prog,
            name=cls._parser.prog.replace("-", "_").replace("/", "_")
        ))

    @classmethod
    def main(cls):
        cls._parser = ArgumentParser(prog=cls.prog)
        if cls.version:
            cls._parser.add_argument('--version', "-V", action='version', version=cls.version)
        cls._parser.set_defaults(sub_cmd_func=None)

        cls.main_parser(cls._parser)

        subparsers = cls._parser.add_subparsers(metavar="", help='', title="Commands")
        for i in Cmd._all:
            i.init_parser(subparsers)

        if cls.complete:
            cls.complete_init(subparsers)

        arg = cls._parser.parse_args()

        cls.main_args(arg)

        if not arg.sub_cmd_func:
            cls._parser.print_help()
            return
        arg.sub_cmd_func(arg)

    @classmethod
    def main_parser(cls, parser: ArgumentParser):
        pass

    @classmethod
    def main_args(cls, args):
        pass
