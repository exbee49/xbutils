import json


def to_html(txt: str) -> str:
    """ Replace <,>,& to html equivalent """
    return (txt.replace('&', '&amp;').replace("<", "&lt;")
            .replace(">", "&gt;").replace("\n", '<br>\n'))


class HtmlWriter:
    _buffer: list[str]

    _buffer: list[str]
    _tag_stack: list[str]
    _state_stack: list[int]
    _next_id: int = 0

    def __init__(self):
        self._buffer = list()
        self._tag_stack = list()
        self._state_stack = list()

    def clear(self):
        self._buffer.clear()
        self._tag_stack.clear()
        self._state_stack.clear()
        if self._next_id:
            self._next_id = 0

    def get_text(self):
        self.end(1000)
        return ''.join(self._buffer)

    def write(self, *p) -> "HtmlWriter":
        self._buffer.extend(map(str, p))
        return self

    __call__ = write

    def text(self, *p) -> "HtmlWriter":
        self._buffer.extend(to_html(str(i)) for i in p)
        return self

    def tag(self, __name: str, **__kwarg) -> "HtmlWriter":
        """ tag without stack"""
        self.write('<' + __name)
        for k, v in __kwarg.items():
            if v is False:
                continue
            if k[-1:] == '_':
                k = k[:-1]
            if v is True:
                v = k

            self.write(f' {k}="{v}"')
        self.write('>')
        return self

    def stag(self, __name: str, **__kwarg) -> "HtmlWriter":
        """ tag with stack"""
        self.tag(__name, **__kwarg)
        self._tag_stack.append(__name)
        return self

    def end(self, n: int = 1) -> "HtmlWriter":
        """ remove n entities from stack """
        while self._tag_stack and n > 0:
            n -= 1
            self.write(f'</{self._tag_stack.pop(-1)}>')
        return self

    def state_push(self) -> "HtmlWriter":
        """ save entities stack state """
        self._state_stack.append(len(self._tag_stack))
        return self

    def state_pop(self) -> "HtmlWriter":
        """ close entities opened since last push"""
        if self._state_stack:
            n = self._state_stack.pop(-1)
            while len(self._tag_stack) > n:
                self.end()

        return self

    def ul(self, **__kwarg) -> "HtmlWriter":
        """ html ul """
        return self.stag("ul", **__kwarg)

    def li(self, **__kwarg) -> "HtmlWriter":
        return self.stag("li", **__kwarg)

    def li_text(self, *__text, **__kwargs) -> "HtmlWriter":
        return self.li(**__kwargs).text(*__text).end()

    def li_link(self, url, *__text, **__kwargs) -> "HtmlWriter":
        return self.li(**__kwargs).a_text(*__text, href=url).end()

    def li_blink(self, url, *__text, **__kwargs) -> "HtmlWriter":
        return self.li(**__kwargs).a_text(*__text, href=url, target="_blank").end()

    def div(self, **__kwarg) -> "HtmlWriter":
        return self.stag("div", **__kwarg)

    def div_text(self, *__text, **__kwargs) -> "HtmlWriter":
        return self.div(**__kwargs).text(*__text).end()

    def div_link(self, url, *__text, **__kwargs) -> "HtmlWriter":
        return self.div(**__kwargs).a_text(*__text, href=url).end()

    def form(self, **__kwarg) -> "HtmlWriter":
        return self.stag("form", **__kwarg)

    def hr(self, **__kwarg) -> "HtmlWriter":
        return self.tag("hr", **__kwarg)

    def br(self, **__kwarg) -> "HtmlWriter":
        return self.tag("br", **__kwarg)

    def input(self, type_='text', label: str = "", **__kwarg) -> "HtmlWriter":
        ni = None
        label_after = False
        if label:
            ni = self._attr_id(__kwarg)
            if type_.lower() in ('radio', 'checkbox'):
                label_after = True
            else:
                self.label_text(label, for_=ni)

        self.tag("input", type_=type_, **__kwarg)
        if label_after:
            self.label_text(label, for_=ni)

        return self

    def submit(self, **__kwarg) -> "HtmlWriter":
        return self.input('submit', **__kwarg)

    def checkbox(self, **__kwarg) -> "HtmlWriter":
        return self.input('checkbox', **__kwarg)

    def input_hidden(self, name: str, value: str) -> "HtmlWriter":
        return self.input('hidden', name=name, value=value)

    def label(self, **__kwarg) -> "HtmlWriter":
        return self.stag('label', **__kwarg)

    def label_text(self, *__text, **__kwargs) -> "HtmlWriter":
        return self.label(**__kwargs).text(*__text).end()

    def a(self, **__kwarg) -> "HtmlWriter":
        return self.stag('a', **__kwarg)

    def a_text(self, *__text, **__kwargs) -> "HtmlWriter":
        return self.a(**__kwargs).text(*__text).end()

    def span(self, **__kwarg) -> "HtmlWriter":
        return self.stag('span', **__kwarg)

    def span_text(self, *__text, **__kwargs) -> "HtmlWriter":
        return self.span(**__kwargs).text(*__text).end()

    def select(self, values=None, **__kwargs) -> "HtmlWriter":
        self.stag("select", **__kwargs)
        if values is None:
            return self
        for i in values:
            if isinstance(i, tuple):
                text, value = i
            else:
                value = text = i
            self.option(text, value=value)
        return self.end()

    def option(self, *__text, **__kwargs) -> "HtmlWriter":
        self.stag("option", **__kwargs)
        if not len(__text):
            return self
        return self.text(*__text).end()

    def new_id(self):
        self._next_id += 1
        return f'_id{self._next_id}'

    def _attr_id(self, attr: dict):
        if 'id' in attr:
            return attr['id']
        if 'id_' in attr:
            return attr['id_']
        ni = self.new_id()
        attr["id_"] = ni
        return ni

    def nl(self) -> "HtmlWriter":
        self._buffer.append('\n')
        return self

    def html(self, title: str = "", css: str = '', js: str = "") -> "HtmlWriter":
        self.clear()
        self.write('<!DOCTYPE html>\n<html>\n<head>\n'
                   '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                   "<title>", to_html(title), '</title>\n')
        if css:
            self.write(f'<link rel="stylesheet" href="{css}" />\n')
        if js:
            self.write(f'<script src="{js}"></script>\n')
        self.write("</head><body>\n")
        self._tag_stack = ["html", 'body']
        return self

    # ============== script =====================
    def script(self, **__kwarg) -> "HtmlWriter":
        """script tag"""
        return self.stag('script', **__kwarg)

    def script_text(self, *__text, **__attr) -> "HtmlWriter":
        """
        script with text

        :param __text: script text
        :param __attr: add values as const
        """
        self.script().nl()
        for k, v in __attr.items():
            self(f"const {k}={json.dumps(v)};\n")
        self(*__text)
        return self.end()

    @staticmethod
    def to_html(text: str) -> str:
        return to_html(text)

    def __enter__(self):
        self.state_push()
        return self

    def __exit__(self, *args):
        self.state_pop()
        return False


def _main_test():
    w = HtmlWriter()
    w.html(title="titleœ")
    print(w.get_text())


if __name__ == '__main__':
    _main_test()
