"""
Top level of the system.
"""

from core import call, trampoline, final_k
import primitives; primitives.install()
from environments import GlobalEnv
from parse_sans_offsides import parse

def run(text):
    expr, = parse(text)
    return trampoline(expr.eval(global_env, final_k))

global_env = GlobalEnv({})

global_env.adjoin('no', False)
global_env.adjoin('yes', True)

class Parse(object):
    vtable = {('of',): lambda rcvr, (text,), k: (k, parse(primitives.as_string(text))[0])}

global_env.adjoin('parse', Parse())


# Testing

## run("parse of '2+3'")
#. {(2 + 3)}

## run('42')
#. 42
## run('2+3')
#. 5

## run('a ::= 2; a * 3')
#. 6

text3 = """
empty :: {
   size: { 0 } };
push of element on stack :: {
   :: { size: { 1 + stack size } } };
(push of 'a' on (push of 'b' on empty)) size
"""
## run(text3)
#. 2

fact = """
factorial of n :: {
   (0 = n) if-so:  { 1 }
           if-not: { n * (factorial of (n - 1)) }
};
factorial of 5
"""
## run(fact)
#. 120
