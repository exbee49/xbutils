"""
sub commands argparse helper

Example::

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

bash autocompletion::

    eval "$(python myscript.py complete-bash)"
    # or
    python myscript.py complete-bash >> ~/.bashrc



"""

from typing import Union, Callable, Sequence, Optional
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


class Param:
    """
    Argument definition
    """

    def __init__(self, *__args, **__kwarg) -> None:
        self.args = __args
        self.kwarg = __kwarg

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(*self.args, **self.kwarg)


class Cmd:
    """
    Sub command definition

    A class with a name will be instantiated

    """
    _all: list["Cmd"] = list()

    #: version string
    version: str = ""

    #: ArgumentParser prog definition
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
    help: Optional[str] = ""

    #: Help string (in command help)
    desc: str = ""

    #: Complete for cmd
    cmd_complete: list[str] = []

    #: parameters
    params: Sequence[Param] = ()

    _parser: ArgumentParser = None

    # noinspection PyShadowingBuiltins
    def __init__(self, name: Union[None, str, Sequence[str]] = None,
                 function: Union[str, Callable, None] = None, help: Optional[str] = None,
                 desc: Optional[str] = None, params: Union[Param, Sequence[Param], None] = None) -> None:
        """

        :param name:
        :param function:
        :param help:
        :param desc:
        :param params:
        """
        super().__init__()
        if name is not None:
            self.name = name
        if function is not None:
            self.function = function
        if help is not None:
            self.help = None if help == "HIDDEN" else help
        if desc is not None:
            self.desc = desc

        if isinstance(self.name, str):
            self.name = [self.name]

        if params is not None:
            if isinstance(params, Param):
                self.params = (params,)
            else:
                self.params = params

        self._all.append(self)

    def __call__(self, func: Callable) -> Callable:
        """
        As decorator
        """
        self.function = func
        return func

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
        for p in self.params:
            p.add_arguments(parser)

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
        if callable(cls.function):
            cls.function = staticmethod(cls.function)
        if cls.name is not None:
            cls()

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
        func = arg.sub_cmd_func
        del arg.sub_cmd_func
        func(arg)

    @classmethod
    def main_parser(cls, parser: ArgumentParser):
        pass

    @classmethod
    def main_args(cls, args):
        pass
