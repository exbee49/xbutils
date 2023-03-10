import re

from typing import Optional


class TemplateError(Exception):
    pass


class TemplateNotFound(TemplateError):
    pass


class Template:
    _mgr: Optional['TmplMgr'] = None
    _text: str

    regexp = re.compile('(<<<(.*?)>>>)', re.A)

    def process(self) -> str:
        start = 0
        result = list()

        while True:
            m = self.regexp.search(self._text, start)
            if m is None:
                result.append(self._text[start:])
                break
            result.append(self._text[start:m.start()])
            start = m.end()
            result.append(self.get_value(m.group(2)))

        return ''.join(result)

    def get_value(self, value: str):
        print(value)
        return '[' + value + ']'

    def __init__(self, text: str, mgr: Optional['TmplMgr']) -> None:
        self._text = text
        if mgr is not None:
            self._mgr = mgr


class TmplMgr:
    _tmpl_class = Template

    _text: dict[str, str] = None

    def __init__(self) -> None:
        self._cache = dict()
        self._text = dict()

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
