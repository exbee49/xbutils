from xbutils.template import TmplMgr

mgr = TmplMgr()


mgr.add_text("tmpl1","""
template 1
><<<titi>>><
sssss
<<<toto>>>

""")


print(mgr.get_template("tmpl1").process())
