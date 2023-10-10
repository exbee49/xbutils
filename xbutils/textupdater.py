from pathlib import Path
from typing import Union, Optional
import re


class TagFinder:
    pos_tag = ('', 'START ', 'END ')

    class Reply:

        def __init__(self, v):
            super().__init__()
            self._v = v

        def update(self, text: str, value: str):
            return self._v[0].update(text, value, self._v[1:])

    def __init__(self, start: str, end: str = ""):
        super().__init__()
        self._find = (r'^\s*(' + self.escape(re.escape(start) + r'\s+') + '{tag}'
                      + self.escape((r'\s+' if end else '') + re.escape(end) + r'\s*$)'))
        e_start = self.escape(start)
        e_end = ' ' + self.escape(end) if end else ""

        self._full = (e_start + ' ' + self.pos_tag[1] + '{tag}' + e_end + '\n{text}\n' + e_start + ' ' +
                      self.pos_tag[2] + '{tag}' + e_end)
        self._empty = e_start + ' ' + self.pos_tag[0] + '{tag}' + e_end

    def find(self, text: str, tag: str):
        e_tag = re.escape(tag)

        def _find(pos: int = 0):
            req = self._find.format(tag=self.pos_tag[pos] + e_tag)
            m = re.search(req, text, re.MULTILINE)
            return (None, None) if m is None else m.span(1)

        a, b = _find(0)
        if a is None:
            a, _ = _find(1)
            if a is None:
                return None
            _, b = _find(2)
            if b is None:
                return None
        return self.Reply((self, a, b, tag))

    def update(self, text, value, rep):
        a, b, tag = rep
        if value:
            return text[:a] + self._full.format(tag=tag, text=value) + text[b:]
        else:
            return text[:a] + self._empty.format(tag=tag) + text[b:]

    @staticmethod
    def escape(s: str):
        return s.replace("{", "{{").replace('}', '}}')


class TextUpdater:
    _path: Optional[Path] = None
    _text: Optional[str] = None
    _eol: str = ""

    tag_finder = [
        TagFinder("<!--", '-->'),
        TagFinder("/*", '*/'),
        TagFinder("#"),
        TagFinder("//"),

    ]

    def __init__(self, path: Union[None, str, Path] = None, text: Optional[str] = None):
        super().__init__()
        if text is None:
            if path is not None:
                self.open(path)
        else:
            if path is not None:
                self._path = Path(path).resolve()
            self.set_text(text)

    def set_text(self, text):
        self._text = text
        if '\r' in self._text:
            self._text = self._text.replace('\r', '')
            self._eol = '\n\r'
        elif self._eol:
            self._eol = ''

    def open(self, path: Union[str, Path]):
        self._path = Path(path).resolve()
        self.set_text(self._path.read_text())

    def text(self):
        return self._text.replace('\n', self._eol) if self._eol else self._text

    def write(self, path: Union[None, str, Path] = None):
        path = self._path if path is None else Path(path).resolve()
        path.write_text(self.text())

    def _find_tag(self, tag: str):
        for i in self.tag_finder:
            r = i.find(self._text, tag)
            if r is not None:
                return r

    def update(self, field: str, text: str = '') -> bool:
        rep = self._find_tag(field)
        if rep is None:
            return False
        self._text = rep.update(self._text, text)
        return True


def _test_update():
    text = '''
    START
    # TAG1
    ------
    <!-- TAG2 -->
    END
    '''

    u = TextUpdater(text=text)
    u.update('TAG1', 'tag1.1\ntag1.2')
    u.update('TAG2', 'tag2.1\ntag2.2')
    print(u.text())
    u.update('TAG1', 'TAG1 CONTENT')
    print(u.text())
    u.update('TAG1')
    u.update('TAG2')
    print(u.text())
    print(u.text() == text)


if __name__ == '__main__':
    _test_update()
