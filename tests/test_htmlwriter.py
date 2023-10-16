from unittest import TestCase, main


class TestHtmlWriter(TestCase):

    def test_import(self):
        from xbutils.htmlwriter import HtmlWriter
        HtmlWriter()

    def test_basic(self):
        from xbutils.htmlwriter import HtmlWriter
        self.assertEqual(
            HtmlWriter().div().span_text("<>", "uu").get_text(),
            '<div><span>&lt;&gt;uu</span></div>'

        )

    def test_context(self):
        from xbutils.htmlwriter import HtmlWriter
        w = HtmlWriter()
        w("t1").div()
        with w:
            w.div().text("t2")
        w('t3')
        self.assertEqual(
            w.get_text(),
            't1<div><div>t2</div>t3</div>'
        )

    def test_state_context(self):
        from xbutils.htmlwriter import HtmlWriter
        w = HtmlWriter()
        w("t1").div()
        with w.state():
            w.div().text("t2")
        w('t3')
        self.assertEqual(
            w.get_text(),
            't1<div><div>t2</div>t3</div>'
        )

    def test_simple_div_list(self):
        from xbutils.htmlwriter import HtmlWriter

        self.assertEqual(
            HtmlWriter().simple_div_list(("L1", "L2", "L3"))("E").get_text(),
            "<div><div>L1</div>\n<div>L2</div>\n<div>L3</div>\n</div>E"
        )

    def test_simple_ul(self):
        from xbutils.htmlwriter import HtmlWriter

        self.assertEqual(
            HtmlWriter().simple_ul(("L1", "L2", "L3"))("E").get_text(),
            '<ul><li>L1</li>\n<li>L2</li>\n<li>L3</li>\n</ul>E'
        )

    def test_simple_table(self):
        from xbutils.htmlwriter import HtmlWriter
        self.assertEqual(
            HtmlWriter().simple_table([["I11", "I12"], ["I2"]])("E").get_text(),
            "<table><tbody><tr><td>I11</td><td>I12</td></tr>\n<tr><td>I2</td></tr>\n</tbody></table>E"
        )


if __name__ == '__main__':
    main()
