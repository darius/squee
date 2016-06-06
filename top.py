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

global_env.adjoin('global-environment', global_env)

class Claim(object):
    vtable = {('from',): lambda rcvr, (x,), k: (k, primitives.as_bool(x))}

global_env.adjoin('no', False)
global_env.adjoin('yes', True)
global_env.adjoin('Claim', Claim())

class MakeList(object):
    entuple = lambda rcvr, args, k: (k, args)
    vtable = {('of',): entuple,
              ('of','and'): entuple,
              ('of','and','and'): entuple}

global_env.adjoin('nil', ())
global_env.adjoin('make-list', MakeList())

class Parse(object):
    vtable = {('of',): lambda rcvr, (text,), k: (k, parse(primitives.as_string(text))[0])}

global_env.adjoin('parse', Parse())


# Testing

## run('42')
#. 42
## run('2+3')
#. 5

## run('a ::= 2; a * 3')
#. 6

eg_stack = """
empty :: {
   size: { 0 } };
push of element on stack :: {
   :: { size: { 1 + stack size } } };
(push of 'a' on (push of 'b' on empty)) size
"""
## run(eg_stack)
#. 2

fact = """
so :: {
   if claim then on-yes else on-no: {
      (Claim from claim) if-so on-yes if-not on-no
   }
};
factorial of n :: {
   so if (0 = n) then: { 1 }
                 else: { n * factorial of (n - 1) }
};
factorial of 5
"""
## run(fact)
#. 120

## run("global-environment at 'no'")
#. False
## run("(make-list of 42 and 137) ++ (make-list of 'hello')")
#. (42, 137, 'hello')
## run("parse of '2+3'")
#. {2 + 3}
## run("(parse of '2+3') run-in global-environment")
#. 5

## sets = open('sets.squee').read()
## run(sets)
#. (False, True)
