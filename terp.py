"""
AST interpreter
"""

from collections import namedtuple
import itertools

def trampoline(state):
    k, value = state
    while k is not None:
#        traceback((k, value))
        fn, free_var, k = k
        k, value = fn(value, free_var, k)
    return value

def traceback(state):
    k, value = state
    print ':', value
    while k:
        fn, free_var, k = k
        if isinstance(free_var, tuple) and free_var:
            for i, element in enumerate(free_var):
                print '%-18s %r' % (('' if i else fn.__name__), element)
        else:
            print '%-18s %r' % (fn.__name__, free_var)

def call(receiver, selector, arguments, k):
    methods = get_vtable(receiver)
    if methods.get(selector) is None:
        methods = miranda_methods
    # TODO: handle method-missing
    return methods[selector](receiver, arguments, k)

def get_vtable(x):
    if   isinstance(x, Thing):     return x.vtable
    elif isinstance(x, bool):      return bool_vtable
    elif isinstance(x, num_types): return num_vtable
    elif isinstance(x, str_types): return string_vtable
    elif x is None:                return nil_vtable # TODO: define
    else:                          assert False, "Classless datum"

str_types = (str, unicode)
num_types = (int, long, float)

class Thing(object):
    def __init__(self, env, vtable):
        self.env = env
        self.vtable = vtable
    def __repr__(self):
        return '<%r %r>' % (self.env, self.vtable)

class Method(namedtuple('_Method', 'selector params expr')):
    def __call__(self, receiver, arguments, k):
        return self.expr.eval(receiver.env.extend(self.params, arguments), k)
    def __repr__(self):
        return '%r: %r' % (self.params, self.expr)

class GlobalEnv(namedtuple('_GlobalEnv', 'rib')):
    def adjoin(self, key, value):
        self.rib[key] = value
    def get(self, key):
        return self.rib[key]
    def extend(self, variables, values):
        return Env(dict(zip(variables, values)), self)
    def __repr__(self):
        return 'GlobalEnv'

undefined = object()

class Env(namedtuple('_Env', 'rib container')):
    def define(self, key, value):
        assert key not in self.rib
        assert value is not undefined
        self[key] = value
    def get(self, key):
        return self.rib[key] if key in self.rib else self.container.get(key)
    def extend(self, variables, values):
        return Env(dict(zip(variables, values)), self)
    def __repr__(self):
        return 'Env(%r) / %r' % (self.rib, self.container)

num_vtable = {'+': lambda rcvr, (other,), k: (k, rcvr + as_number(other)),
              '*': lambda rcvr, (other,), k: (k, rcvr * as_number(other)),
              '-': lambda rcvr, (other,), k: (k, rcvr - as_number(other)),
              '=': lambda rcvr, (other,), k: (k, rcvr == other), # XXX object method
              '<': lambda rcvr, (other,), k: (k, rcvr < other),
             }

def as_number(thing):
    if isinstance(thing, num_types):
        return thing
    assert False, "Not a number: %r" % (thing,)

def find_default(rcvr, (other, default), k):
    try:
        return k, rcvr.index(other)
    except ValueError:
        return call(default, 'value', (), k)

def has(rcvr, (other,), k):  return (k, other in rcvr)
def at(rcvr, (i,), k):       return (k, rcvr[i])
def find(rcvr, (other,), k): return (k, rcvr.index(other))
def size(rcvr, _, k):        return (k, len(rcvr))
def add(rcvr, (other,), k):  return (k, rcvr + other)
def eq(rcvr, (other,), k):   return (k, rcvr == other)
def lt(rcvr, (other,), k):   return (k, rcvr < other)

def as_string(thing):
    if isinstance(thing, str_types):
        return thing
    assert False, "Not a string: %r" % (thing,)

string_vtable = {'has:':  has,
                 'at:':   at,
                 'find:': find,
                 'find:default:': find_default,
                 'size':  size,
                 '++':    add,
                 '=':     eq,
                 '<':     lt,
                }

class Constant(namedtuple('_Constant', 'value')):
    def eval(self, env, k):
        return k, self.value
    def defs(self):
        return ()
    def __repr__(self):
        return repr(self.value)

class Fetch(namedtuple('_Fetch', 'name')):
    def eval(self, env, k):
        return (k, env.get(self.name))
    def defs(self):
        return ()
    def __repr__(self):
        return str(self.name)

class Seclude(object):
    def __init__(self, expr):
        self.expr = expr
        self.vars = expr.defs()
        assert len(set(self.vars)) == len(self.vars)
    def defs(self):
        return ()
    def eval(self, env, k):
        vals = [undefined for _ in self.vars]
        return self.expr.eval(env.extend(self.vars, vals), k)
    def __repr__(self):
        return '{%r}' % (self.expr,)

class Define(object):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def defs(self):
        return (self.var,)
    def eval(self, env, k):
        return self.expr.eval(env, (define_k, (env, self), k))
    def __repr__(self):
        return '%s ::= %r' % (self,var, self.expr)

def define_k(value, (env, self), k):
    env.define(self,var, value)
    return (k, value)

class Actor(object):
    def __init__(self, methods):
        self.vtable = {method.selector: method for method in methods}
    def eval(self, env, k):
        return (k, Thing(env, self.vtable))
    def defs(self):
        return ()
    def __repr__(self):
        return repr(sorted(self.vtable.values(), key=lambda m: m.selector))

class Call(namedtuple('_Call', 'subject selector operands')):
    def eval(self, env, k):
        return self.subject.eval(env,
                                 (evrands_k, (self, env), k))
    def defs(self):
        return sum((expr.defs() for expr in (self.subject,) + self.operands),
                   ())
    def __repr__(self):
        return call_repr(self)

def call_repr(self, sep=''):
    subject = repr(self.subject) + sep
    if len(self.operands) == 0:
        return '(%s %s)' % (subject, self.selector)
    elif len(self.operands) == 1:
        return '(%s %s %r)' % (subject, self.selector, self.operands[0])
    else:
        pairs = zip(self.selector.split(':'), self.operands)
        return '(%s%s)' % (subject, ''.join(' %s: %r' % pair for pair in pairs))

def evrands_k(subject, (self, env), k):
    return evrands(self.operands, env, (call_k, (subject, self), k))

def call_k(arguments, (subject, self), k):
    return call(subject, self.selector, arguments, k)

def evrands(operands, env, k):
    if not operands:
        return k, ()
    else:
        return operands[0].eval(env, (evrands_more_k, (operands[1:], env), k))

def evrands_more_k(val, (operands, env), k):
    return evrands(operands, env, (evrands_cons_k, val, k))

def evrands_cons_k(vals, val, k):
    return k, (val,)+vals

class Then(namedtuple('_Then', 'expr1 expr2')):
    def eval(self, env, k):
        return self.expr1.eval(env, (then_k, (self, env), k))
    def defs(self):
        return self.expr1.defs() + self.expr2.defs()
    def __repr__(self):
        return '%r. %r' % (self.expr1, self.expr2)

def then_k(_, (self, env), k):
    return self.expr2.eval(env, k)

global_env = GlobalEnv({})

bool_vtable  = {'if-so:if-not:': lambda rcvr, args, k: call(args[not rcvr], 'value', (), k)}

global_env.adjoin('no',  False)
global_env.adjoin('yes', True)

final_k = None


# Testing

smoketest_expr = Call(Constant(2), '+', (Constant(3),))
smoketest = smoketest_expr.eval(None, final_k)
## trampoline(smoketest)
#. 5

def emblock(expr):
    return Actor([Method('value', (), expr)])

factorial_body = Call(Call(Fetch('n'), '=', (Constant(0),)),
                      'if-so:if-not:',
                      (emblock(Constant(1)),
                       emblock( # n * (factorial of: (n - 1))
                           Call(Fetch('n'), '*',
                                (Call(Fetch('factorial'), 'of:',
                                      (Call(Fetch('n'), '-', (Constant(1),)),)),)))))
factorial = Actor([Method('of:', ('n',), factorial_body)])
global_env.adjoin('factorial', trampoline(factorial.eval(global_env, final_k)))
try_factorial = Call(Fetch('factorial'), 'of:', (Constant(5),))
## trampoline(try_factorial.eval(global_env, final_k))
#. 120
