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


# Testing

## run('42')
#. 42
## run('2 + 3')
#. 5

fact = """
factorial of n :: {
   (0 = n) if-so:  { 1 }
           if-not: { n * (factorial of (n - 1)) }
};
factorial of 5
"""
## run(fact)
#. 120
