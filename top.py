"""
Top level of the system.
"""

from core import call, trampoline, final_k
from environments import GlobalEnv
import absyntax as A
import primitives; primitives.install()

global_env = GlobalEnv({})

global_env.adjoin('no', False)
global_env.adjoin('yes', True)


# Testing

smoketest_expr = A.Call(A.Constant(2), ('+',), (A.Constant(3),))
smoketest = smoketest_expr.eval(None, final_k)
## trampoline(smoketest)
#. 5

def emblock(expr):
    return A.Actor([A.Method(('run',), (), expr)])

factorial_body = A.Call(A.Call(A.Fetch('n'), ('=',), (A.Constant(0),)),
                      ('if-so', 'if-not'),
                      (emblock(A.Constant(1)),
                       emblock( # n * (factorial of: (n - 1))
                           A.Call(A.Fetch('n'), ('*',),
                                (A.Call(A.Fetch('factorial'), ('of',),
                                      (A.Call(A.Fetch('n'), ('-',), (A.Constant(1),)),)),)))))
factorial = A.Actor([A.Method(('of',), ('n',), factorial_body)])
global_env.adjoin('factorial', trampoline(factorial.eval(global_env, final_k)))
try_factorial = A.Call(A.Fetch('factorial'), ('of',), (A.Constant(5),))
## trampoline(try_factorial.eval(global_env, final_k))
#. 120
