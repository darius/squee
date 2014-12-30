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
global_env.adjoin('nil', ())
global_env.adjoin('global-environment', global_env)

class MakeList(object):
    entuple = lambda rcvr, args, k: (k, args)
    vtable = {('of',): entuple,
              ('of','and'): entuple,
              ('of','and','and'): entuple}

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
factorial of n :: {
   (0 = n) if-so:  { 1 }
           if-not: { n * factorial of (n - 1) }
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
#. {(2 + 3)}
## run("(parse of '2+3') run-in global-environment")
#. 5

## sets = open('sets.squee').read()
## run(sets)
#. Traceback (most recent call last):
#.   File "top.py", line 12, in run
#.     return trampoline(expr.eval(global_env, final_k))
#.   File "/home/darius/git/squee/core.py", line 12, in trampoline
#.     k, value = fn(value, free_var, k)
#.   File "/home/darius/git/squee/absyntax.py", line 125, in call_k
#.     return call(subject, self.cue, arguments, k)
#.   File "/home/darius/git/squee/core.py", line 33, in call
#.     method = miranda_methods[selector] # TODO: handle method-missing
#. KeyError: ('||',)
