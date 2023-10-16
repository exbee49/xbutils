from unittest import TestCase, main

text1_1 = '''
START
# TAG1
------
<!-- TAG2 -->
END
'''

text1_2 = '''
START
# START TAG1
TTT
# END TAG1
------
<!-- START TAG2 -->
TTT
<!-- END TAG2 -->
END
'''

text1_3 = '''
START
# START TAG1
U
# END TAG1
------
<!-- START TAG2 -->
U
<!-- END TAG2 -->
END
'''

text2_1 = """
Testt

DDDD
"""

text2_2 = text2_1 + """
# START TAG
UUU
# END TAG
"""

text2_3 = text2_1 + """
# START TAG
X
# END TAG
"""

text2_4 = text2_1 + """
# TAG
"""


class TestTextUpdater(TestCase):

    def test_import(self):
        # noinspection PyUnresolvedReferences
        import xbutils.textupdater

    def test_updater(self):
        from xbutils.textupdater import TextUpdater

        u = TextUpdater(text=text1_1)
        u.update('TAG1', "TTT")
        u.update('TAG2', "TTT")
        self.assertFalse(u.update('TAG3', 'VALUE'))
        self.assertEqual(u.text(), text1_2)
        u.update('TAG1', "U")
        u.update('TAG2', "U")
        self.assertEqual(u.text(), text1_3)
        u.update('TAG1')
        u.update('TAG2')
        self.assertEqual(u.text(), text1_1)

    def test_bash_updater(self):
        from xbutils.textupdater import BashUpdater
        u = BashUpdater(text=text2_1)
        u.update('TAG', "UUU")
        self.assertEqual(u.text(), text2_2)
        u.update('TAG', "X")
        self.assertEqual(u.text(), text2_3)
        u.update('TAG')
        self.assertEqual(u.text(), text2_4)


if __name__ == '__main__':
    main()
