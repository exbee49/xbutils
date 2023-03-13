import re

from typing import Optional, Any, Callable

# TODO: code in template
# TODO: write template to file
# TODO: template from file or dir

class TemplateError(Exception):
    """Base Exception"""


class TemplateNotFound(TemplateError):
    """Unknown template"""


class TemplateEvalError(TemplateError):
    """Template exception during eval"""


class TextFunc:
    def __init__(self, func: Callable):
        self._func = func

    def __str__(self):
        return str(self._func())


class Template:
    _mgr: Optional['TmplMgr'] = None
    _text: str

    regexp = re.compile('(<<<(.*?)>>>)', re.A)

    def __init__(self, text: str, mgr: Optional["TmplMgr"] = None) -> None:
        if mgr is not None:
            self._mgr = mgr
        self._text = text

    def format(self, __dict: Optional[dict[str, Any]] = None, **__kwarg):
        args = self._mgr.get_values().copy() if self._mgr else dict()
        if __dict:
            args.update(__dict)
        args.update(__kwarg)
        return self.parse(args)

    def parse(self, args: dict[str, Any]) -> str:

        start = 0
        result = list()

        while True:
            m = self.regexp.search(self._text, start)
            if m is None:
                result.append(self._text[start:])
                break
            result.append(self._text[start:m.start()])
            start = m.end()
            result.append(self.parse_field(m.group(2), args))

        return ''.join(result)

    def parse_field(self, field: str, args: dict[str, Any]):
        if not field:
            return '<<<'
        if field[:1] == "!":
            return self.eval_field(field[1:], args)
        return self.get_value(field, args)

    # noinspection PyMethodMayBeStatic
    def get_value(self, field: str, args: dict[str, Any]):
        if field in args:
            return str(args[field])
        if '__default__' in args:
            return str(args["__default__"])
        print(f"*ERR* missing value {field}")
        return f'<<<?{field}>>>'

    # noinspection PyMethodMayBeStatic
    def eval_field(self, field: str, args: dict[str, Any]):
        edict = args.copy()
        edict.update(get_value=self.get_value)
        try:
            return str(eval(field, edict))
        except Exception as err:
            raise TemplateEvalError(f"Eval Error for {field} : {err}")


class TmplMgr:
    _tmpl_class = Template

    _text: dict[str, str] = None
    _values: dict[str, Any] = None

    def __init__(self) -> None:
        self._cache = dict()
        self._text = dict()
        self._values = dict()

    def add_text(self, name, text):
        self._text[name] = text

    def create_template(self, text: str) -> Template:
        return self._tmpl_class(text, mgr=self)

    def get_template_text(self, name: str) -> str:
        if name in self._text:
            return self._text[name]
        raise TemplateNotFound(f'Template Not found: {name}')

    def get_template(self, name: str) -> Template:
        text = self.get_template_text(name)
        reply = self.create_template(text)
        return reply

    def get_values(self) -> dict[str, Any]:
        return self._values

    def set_value(self, __dict: Optional[dict[str, Any]] = None, **__kwarg) -> None:
        if __dict:
            self._values.update(__dict)
        self._values.update(__kwarg)

    def format(self, __tmpl: str, __dict: Optional[dict[str, Any]] = None, **__kwarg) -> str:
        return self.get_template(__tmpl).format(__dict, **__kwarg)
