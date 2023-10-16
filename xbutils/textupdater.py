"""
Update text or file.

Replace special comments with text

* `TextUpdater` : main class
* `BashUpdater` : updater for bash scripts

example::

    text = '''
    some text
    # MYTAG
    another text
    '''

    u = TextUpdater(text=text)
    u.update('MYTAG', 'tag text')
    print(u.text())

    '''
    some text
    # START MYTAG
    tag text
    # END MYTAG
    another text
    '''

    u.update('MYTAG', 'another tag text')
    print(u.text())

    '''
    some text
    # START MYTAG
    another tag text
    # END MYTAG
    another text
    '''



    u.update('MYTAG')
    print(u.text())

    '''
    some text
    # MYTAG
    another text
    '''

"""

from pathlib import Path
from typing import Union, Optional
import re


class TagFinder:
    """ Find and replace comment

    """

    #: text to add in comment
    pos_tag = ('', 'START ', 'END ')

    class Reply:
        """`TextFinder` find result"""

        def __init__(self, v):
            super().__init__()
            self._v = v

        def update(self, text: str, value: str):
            """ call `TagFinder` update """
            return self._v[0].update(text, value, self._v[1:])

    def __init__(self, start: str, end: str = ""):
        """

        :param start: start comment  ("<!--" for example)
        :param end: end comment  ("-->" for example)
        """
        super().__init__()

        def re_escape(_s: str):
            return re.escape(self.escape(_s))

        self._find = (r'^\s*(' + re_escape(start) + r'\s+(' + '|'.join(map(re_escape, self.pos_tag)) + '){tag}'
                      + self.escape((r'\s+' if end else '') + re.escape(end) + r'\s*?)$'))

        e_start = self.escape(start)
        e_end = ' ' + self.escape(end) if end else ""

        self._full = (e_start + ' ' + self.pos_tag[1] + '{tag}' + e_end + '\n{text}\n' + e_start + ' ' +
                      self.pos_tag[2] + '{tag}' + e_end)
        self._empty = e_start + ' ' + self.pos_tag[0] + '{tag}' + e_end

    def find(self, text: str, tag: str):
        """
        find tag comment in tag

        :param text: text
        :param tag: field name
        :return: Reply or None
        """
        # e_tag = re.escape(tag)
        matches = list((self.pos_tag.index(m.group(2)), m.start(1), m.end()) for m in
                       re.finditer(self._find.format(tag=re.escape(tag)), text, re.MULTILINE))
        if not matches:
            return None

        prev = matches[0]
        for cur in matches[1:]:
            if prev[0] == 1 and cur[0] == 2:
                return self.Reply((self, prev[1], cur[2], tag))
            prev = cur
        for cur in matches:
            if cur[0] == 0:
                return self.Reply((self, cur[1], cur[2], tag))
        return None

    def update(self, text, value, rep):
        a, b, tag = rep
        print("REP", (text[:a], text[a:b], text[b:]))
        return text[:a] + self.build(tag=tag, text=value) + text[b:]

    def build(self, tag: str, text: str) -> str:
        """
        Create a comment block

        :param tag: field name
        :param text: text ro put inside comment block
        """
        if text:
            return self._full.format(tag=tag, text=text)
        return self._empty.format(tag=tag)

    @staticmethod
    def escape(s: str):
        return s.replace("{", "{{").replace('}', '}}')

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class TextUpdater:
    """
    Update text or file.

    Replace special comments with text.

    accept python/sh (#) , c (/star -  star/,//) and html (<!-- -->) comments
    """

    _path: Optional[Path] = None
    _text: Optional[str] = None
    _eol: str = ""

    #: list of `TagFinder`
    tag_finder = [
        TagFinder("<!--", '-->'),
        TagFinder("/*", '*/'),
        TagFinder("#"),
        TagFinder("//"),
    ]

    def __init__(self, path: Union[None, str, Path] = None, text: Optional[str] = None):
        """

        :param path: file path or None
        :param text: text or None
        """
        super().__init__()
        if text is None:
            if path is not None:
                self.open(path)
        else:
            if path is not None:
                self._path = Path(path).resolve()
            self.set_text(text)

    def set_text(self, text):
        """
        set text
        """
        self._text = text
        if '\r' in self._text:
            self._text = self._text.replace('\r', '')
            self._eol = '\n\r'
        elif self._eol:
            self._eol = ''

    def open(self, path: Union[str, Path]):
        """
        open a file

        :param path: file path
        """
        self._path = Path(path).resolve()
        self.set_text(self._path.read_text())

    def text(self):
        """ updated text"""
        return self._text.replace('\n', self._eol) if self._eol else self._text

    def write(self, path: Union[None, str, Path] = None):
        """
        write updated text

        :param path: file path or None
        """
        path = self._path if path is None else Path(path).resolve()
        path.write_text(self.text())

    def _find_tag(self, tag: str):
        for i in self.tag_finder:
            r = i.find(self._text, tag)
            if r is not None:
                return r

    def update(self, field: str, text: str = '') -> bool:
        """
        Update comment block

        :param field: field name
        :param text: text to input inside comment block

        :return: True if field is found
        """
        rep = self._find_tag(field)
        if rep is None:
            return False
        self._text = rep.update(self._text, text)
        return True

    def tag_exists(self, tag: str) -> bool:
        return self._find_tag(tag) is not None


class TextUpdaterAdd(TextUpdater):
    """
    `TextUpdater` that add a comment at end block if it's not found
    """

    def update(self, field: str, text: str = '') -> bool:
        """
        Update or add comment block

        :param field: field name
        :param text: text to input inside comment block

        :return: True
        """
        if not super().update(field, text):
            self._text += '\n' + self.tag_finder[0].build(field, text) + "\n"
        return True


class BashUpdater(TextUpdaterAdd):
    """ `TextUpdaterAdd` for bash scripts """
    tag_finder = [
        TagFinder("#"),
    ]


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
    print(u.update('TAG3'))

    text = '''#Text start   
    '''

    u = BashUpdater(text=text)

    u.update('TAG', 'ls -al')
    print(repr(u.text()))
    u.update('TAG', 'll')
    print(repr(u.text()))
    u.update('TAG')
    print(repr(u.text()))
    u.update('TAG', 'rrr')
    print(repr(u.text()))


if __name__ == '__main__':
    _test_update()
