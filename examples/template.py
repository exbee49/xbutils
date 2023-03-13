from xbutils.template import TmplMgr, TextFunc
from pathlib import Path


def f1():
    return 'FROM F1 FUNCTION'


mgr = TmplMgr()

mgr.add_text("tmpl1", """
template 1
Value:<<<val>>>
TestFunc:<<<ff>>>
Eval:<<<!val+2>>>
Default:<<<notdef>>>
From mgr:<<<mgr_value>>>
""")

mgr.set_value(val=99, mgr_value="FROM MGR")

print(mgr.format("tmpl1", __default__="???", ff=TextFunc(f1), val=42))

mgr.add_dir(Path(__file__).resolve().parent)

print(mgr.format("tmpl2.txt", v1="V1", v2='V2'))
