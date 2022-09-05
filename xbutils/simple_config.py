"""
cfg module
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


    """

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

    def __init__(self) -> None:
        super().__init__()
        self._init()

    def read_config(self, cfg_file: Union[Path, str], must_exist=False) -> bool:
        self._before_read()
        cfg_file = Path(cfg_file).expanduser().resolve()
        if not cfg_file.exists():
            if not must_exist:
                return True
            self._error(f"Missing config file {cfg_file}")
            return False
        ok = True
        local_dict = dict()
        try:
            exec(cfg_file.read_text(encoding="utf8"), dict(Path=Path, config_directory=cfg_file.resolve().parent),
                 local_dict)
        except Exception as v:
            self._error(f"Reading Config: {v}")
            ok = False

        valid_attrs = dict(
            (k, v) for k, v in self.__annotations__.items()
            if k[:1] != '_' and v in (str, int, bool, float, Path)
        )

        for k, v in local_dict.items():
            if k[:1] == "_":
                continue
            if k not in valid_attrs:
                print(f"*WRN* Unknown config value {k}")
                ok = False
                continue
            # noinspection PyTypeHints
            if valid_attrs[k] == Path:
                if isinstance(v, str):
                    v = Path(v)
                    if '~' in str(v):
                        v = v.expanduser()
                elif not isinstance(v, Path):
                    self._error(f"Bad type for config value {k} must be str or Path")
                    ok = False
                    continue
            elif valid_attrs[k] == float:
                if isinstance(v, int):
                    v = float(v)
                elif not isinstance(v, float):
                    self._error(f"Bad type for config value {k} must be a float")
                    ok = False
                    continue
            elif not isinstance(v, valid_attrs[k]):
                self._error(f"*WRN* Bad type for config value {k} must be {valid_attrs[k]}")
                ok = False
                continue
            setattr(self, k, v)
        self._after_read()
        return ok
