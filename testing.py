import pprint
import ast
import astpretty

astpretty.pprint(ast.parse("x * (3+y)"))