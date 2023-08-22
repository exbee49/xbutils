"""
cfg module

Example::

    from xbutils.simple_config import SimpleConfig
    from pathlib import Path


    class Config(SimpleConfig):
        bool_value: bool = True

        path_value: Path = Path("titi.py")
        path_value2: Path = Path("titi.py")

        int_value: int = 22

        float_value: float = 1.0

        str_value: str = "NoValue"


    cfg = Config()

    cfg.read_config("simple_config.cfg", must_exist=True)

    print(cfg.bool_value)
    print(cfg.path_value)
    print(cfg.int_value)

"""
from pathlib import Path
from typing import Union


class SimpleConfig:
    """Simple Config File.

    The attributes must be defined with type::

        class Cfg(SimpleConfig):
            int_value: int = 1
            bool_value: bool = True
            str_value: str = "toto"
            path_value: Path = Path("/usr")
            float_value: float = 1.

    ~ in Path will be expanded


    """
    _config_globals: dict
    _valid_attrs: dict

    @staticmethod
    def _error(text):
        """ override to print error messages"""
        print("*ERR*", text)

    def _init(self):
        """ override to init value (called in __init__)"""
        pass

    def _before_read(self):
        """ hook called before read"""
        pass

    def _after_read(self):
        """ hook called after read"""
        pass

    def _update_globals(self, d: dict):
        """ modify globals (before config)"""
        pass

    def __init__(self) -> None:
        super().__init__()
        self._config_globals = dict(
            Path=Path,
        )
        for i in dir(self):
            func = getattr(self, i)
            if hasattr(func, '_gdf'):
                self._config_globals[func._gdf] = func

        self._valid_attrs = dict(
            (k, v) for k, v in self.__annotations__.items()
            if k[:1] != '_' and v in (str, int, bool, float, Path)
        )

        self._init()

    def read_config(self, cfg_file: Union[Path, str], must_exist=False) -> bool:
        """
        read config file

        :param cfg_file: config file
        :param must_exist: if True, call _error in file doesn't exist
        :return: False on error


        globals::

            Path=Path
            config_file: config file path
            config_directory: config file directory


        """
        self._before_read()
        cfg_file = Path(cfg_file).expanduser().resolve()
        if not cfg_file.exists():
            if not must_exist:
                return True
            self._error(f"Missing config file {cfg_file}")
            return False
        ok = True
        local_dict = dict()
        global_dict = self._config_globals.copy()
        global_dict.update(
            config_file=cfg_file.resolve(),
            config_directory=cfg_file.resolve().parent,
        )
        self._update_globals(global_dict)

        try:
            exec(cfg_file.read_text(encoding="utf8"), global_dict,
                 local_dict)
        except Exception as v:
            self._error(f"Reading Config: {v}")
            ok = False

        for k, v in local_dict.items():
            if k[:1] == "_":
                continue
            if k not in self._valid_attrs:
                print(f"*WRN* Unknown config value {k}")
                ok = False
                continue
            # noinspection PyTypeHints
            if self._valid_attrs[k] == Path:
                if isinstance(v, str):
                    v = Path(v)
                    if '~' in str(v):
                        v = v.expanduser()
                elif not isinstance(v, Path):
                    self._error(f"Bad type for config value {k} must be str or Path")
                    ok = False
                    continue
            elif self._valid_attrs[k] == float:
                if isinstance(v, int):
                    v = float(v)
                elif not isinstance(v, float):
                    self._error(f"Bad type for config value {k} must be a float")
                    ok = False
                    continue
            elif not isinstance(v, self._valid_attrs[k]):
                self._error(f"*WRN* Bad type for config value {k} must be {self._valid_attrs[k]}")
                ok = False
                continue
            setattr(self, k, v)
        self._after_read()
        return ok


def global_def(name: str):
    """Decorator to add a method as global function in config

    :param name: function name


    example::

        class  MyConfig(SimpleConfig):

            @global_def('my_global_func')
            def _a_func(self,p:int):
                print(p)

    """

    def f(func):
        func._gdf = name
        return func

    return f
