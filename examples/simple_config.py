from xbutils.simple_config import SimpleConfig, global_def
from pathlib import Path


class Config(SimpleConfig):
    bool_value: bool = True

    path_value: Path = Path("titi.py")
    path_value2: Path = Path("titi.py")

    int_value: int = 22

    float_value: float = 1.0

    str_value: str = "NoValue"

    @global_def("my_global")
    def _my_global(self, v):
        print("my_global called with", v)


cfg = Config()

cfg.read_config("simple_config.cfg", must_exist=True)

print(cfg.bool_value)
print(cfg.path_value)
print(cfg.int_value)
