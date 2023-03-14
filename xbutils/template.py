import re
from pathlib import Path
from typing import Optional, Any, Callable, Union


# TODO: code in template

class TemplateError(Exception):
    """Base Exception"""


class TemplateNotFound(TemplateError):
    """Unknown template"""


class TemplateEvalError(TemplateError):
    """Template exception during eval"""


class TextFunc:
    """
    Callable Value for :py:obj:`Template`

    Example::

        def func():
            return "test"

        Template("From Func:<<<value>>>").format(value=TextFunc(func))

    """

    def __init__(self, func: Callable):
        self._func = func

    def __str__(self):
        return str(self._func())


class Template:
    """
    Text template.

    Example::

        Template('''
            Simple Value: <<<val1>>>
            Evaluated Value: <<<!val2+2>>>
        ''').format(val1="test",val2=40)
    """
    _mgr: Optional['TmplMgr'] = None
    _text: str

    regexp = re.compile('(<<<(.*?)>>>)', re.A)

    def __init__(self, text: str, mgr: Optional["TmplMgr"] = None) -> None:
        """

        :param text: template text
        :param mgr:  optional Manager
        """
        if mgr is not None:
            self._mgr = mgr
        self._text = text

    def write(self, __dest: Union[Path, str], __dict: Optional[dict[str, Any]] = None, **__kwarg):
        """
        Write a template to file

        :param __dest: destination (can be a directory)
        :param __dict: values as dict
        :param __kwarg: values as arguments
        """

        Path(__dest).write_text(self.format(__dict, **__kwarg))

    def format(self, __dict: Optional[dict[str, Any]] = None, **__kwarg):
        """
        Instantiates a template

        :param __dict: values as dict
        :param __kwarg: values as arguments
        :return: text
        """

        args = self._mgr.get_values().copy() if self._mgr else dict()
        if __dict:
            args.update(__dict)
        args.update(__kwarg)
        return self.parse(args)

    def parse(self, args: dict[str, Any]) -> str:
        """
        Parse template

        :param args: values
        :return: instantiated template
        """

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

    def parse_field(self, field: str, args: dict[str, Any]) -> str:
        """
        parse a field (<<< >>>)

        :param field: field name
        :param args: values
        :return: field value
        """
        if not field:
            return '<<<'
        if field[:1] == "!":
            return self.eval_field(field[1:], args)
        return self.get_value(field, args)

    # noinspection PyMethodMayBeStatic
    def get_value(self, field: str, args: dict[str, Any]):
        """
        :return a value

        :param field: value name
        :param args: values
        :return: value as str
        """
        if field in args:
            return str(args[field])
        if '__default__' in args:
            return str(args["__default__"])
        print(f"*ERR* missing value {field}")
        return f'<<<?{field}>>>'

    # noinspection PyMethodMayBeStatic
    def eval_field(self, field: str, args: dict[str, Any]) -> str:
        """
        Evaluate a field (!field)

        :param field: field without !
        :param args: values
        :return: evaluated field
        """
        edict = args.copy()
        edict.update(get_value=self.get_value)
        try:
            return str(eval(field, edict))
        except Exception as err:
            raise TemplateEvalError(f"Eval Error for {field} : {err}")


class TmplMgr:
    """ Template Manager

    Handles multiple templates
    """
    _tmpl_class = Template

    _texts: dict[str, str] = None
    _files: dict[str, Path] = None
    _dirs: list[Path] = None
    _values: dict[str, Any] = None

    def __init__(self) -> None:
        self._cache = dict()
        self._texts = dict()
        self._files = dict()
        self._dirs = list()
        self._values = dict()

    def add_text(self, name, text):
        """
        Add template from text

        :param name: template name
        :param text: template text
        """
        self._texts[name] = text

    def add_file(self, name: str, path: Union[str, Path]):
        """
        Add template from file

        the template will only be read when necessary

        :param name: template name
        :param path: template file name
        """
        path = Path(path).expanduser().resolve()
        self._files[name] = path

    def add_dir(self, path: Union[str, Path]):
        """
        Look for templates in a directory

        template name is the file name

        :param path: directory path
        """
        path = Path(path).expanduser().resolve()
        self._dirs.append(path)

    def create_template(self, text: str) -> Template:
        """
        create a template

        :param text: text template
        :return: template
        """
        return self._tmpl_class(text, mgr=self)

    def get_template_text(self, name: str) -> str:
        """
        find template text

        :param name: template name
        :return: Template text
        :raise TemplateNotFound: if not found

        """
        if name in self._texts:
            return self._texts[name]
        if name in self._files:
            return self._files[name].read_text()
        for d in self._dirs:
            path = d / name
            if path.is_file():
                return path.read_text()
        raise TemplateNotFound(f'Template Not found: {name}')

    def get_template(self, name: str) -> Template:
        """
        get a template from its name

        :param name: template name
        :return: template
        :raise TemplateNotFound: if not found
        """
        if name in self._cache:
            return self._cache[name]

        text = self.get_template_text(name)
        reply = self.create_template(text)
        self._cache[name] = text
        return reply

    def get_values(self) -> dict[str, Any]:
        """
        Get Manager values

        :return: value
        """
        return self._values

    def set_value(self, __dict: Optional[dict[str, Any]] = None, **__kwarg) -> None:
        """
        set Manager values

        :param __dict: values as dict
        :param __kwarg: values as arguments
        """
        if __dict:
            self._values.update(__dict)
        self._values.update(__kwarg)

    def format(self, __tmpl: str, __dict: Optional[dict[str, Any]] = None, **__kwarg) -> str:
        """
        Instantiates a template

        :param __tmpl: template name
        :param __dict: values as dict
        :param __kwarg: values as arguments
        :return: text
        :raise TemplateNotFound: if not found
        """
        return self.get_template(__tmpl).format(__dict, **__kwarg)

    def write(self, __tmpl: str, __dest: Union[str, Path], __dict: Optional[dict[str, Any]] = None, **__kwarg) -> None:
        """
        Write a template to file

        :param __tmpl: template name
        :param __dest: destination (can be a directory)
        :param __dict: values as dict
        :param __kwarg: values as arguments
        :raise TemplateNotFound: if not found

        """

        dest = Path(__dest)
        if dest.is_dir():
            dest /= __tmpl
        self.get_template(__tmpl).write(dest, __dict, **__kwarg)
