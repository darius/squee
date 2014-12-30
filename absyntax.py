"""
AST interpreter
"""

from collections import namedtuple

from core import call
from environments import extend, undefined

expr_vtable = {
    ('defs',):   lambda self, _, k:      (k, self.defs()),
    ('run-in',): lambda self, (env,), k: self.eval(env, k),
}

class Constant(namedtuple('_Constant', 'value')):
    vtable = expr_vtable
    def defs(self):
        return ()
    def eval(self, env, k):
        return k, self.value
    def __repr__(self):
        return repr(self.value)

class Fetch(namedtuple('_Fetch', 'name')):
    vtable = expr_vtable
    def defs(self):
        return ()
    def eval(self, env, k):
        return k, env.get(self.name)
    def __repr__(self):
        return str(self.name)

class Then(namedtuple('_Then', 'expr1 expr2')):
    vtable = expr_vtable
    def defs(self):
        return self.expr1.defs() + self.expr2.defs()
    def eval(self, env, k):
        return self.expr1.eval(env, (then_k, (self, env), k))
    def __repr__(self):
        return '%r; %r' % (self.expr1, self.expr2)

def then_k(_, (self, env), k):
    return self.expr2.eval(env, k)

class Nest(object):
    vtable = expr_vtable
    def __init__(self, expr):
        self.expr = expr
        self.vars = expr.defs()
        assert len(set(self.vars)) == len(self.vars)
    def defs(self):
        return ()
    def eval(self, env, k):
        vals = [undefined for _ in self.vars]
        return self.expr.eval(extend(env, self.vars, vals), k)
    def __repr__(self):
        return '{%r}' % (self.expr,)

class Define(object):
    vtable = expr_vtable
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def defs(self):
        return (self.var,)
    def eval(self, env, k):
        return self.expr.eval(env, (define_k, (env, self), k))
    def __repr__(self):
        return '%s ::= %r' % (self.var, self.expr)

def define_k(value, (env, self), k):
    env.define(self.var, value)
    return k, value

class Actor(object):
    vtable = expr_vtable
    def __init__(self, methods):
        self.value_vtable = {method.cue: method for method in methods}
    def defs(self):
        return ()
    def eval(self, env, k):
        return k, Thing(env, self.value_vtable)
    def __repr__(self):
        return '{%s}' % '; '.join(sorted(map(repr, self.value_vtable.values())))

class Method(namedtuple('_Method', 'cue params expr')):
    def __call__(self, receiver, arguments, k):
        return self.expr.eval(extend(receiver.env, self.params, arguments), k)
    def __repr__(self):
        if self.params:
            head = '%s %r' % (self.cue, self.params)
        else:
            head = self.cue
        return '%s: %r' % (head, self.expr)

class Thing(object):
    def __init__(self, env, vtable):
        self.env = env
        self.vtable = vtable
    def __repr__(self):
        return '<%r %r>' % (self.env, self.vtable)

class Call(namedtuple('_Call', 'subject cue operands')):
    vtable = expr_vtable
    def defs(self):
        return sum((expr.defs() for expr in (self.subject,) + self.operands),
                   ())
    def eval(self, env, k):
        return self.subject.eval(env, (evrands_k, (self, env), k))
    def __repr__(self):
        subject = repr(self.subject)
        if len(self.operands) == 0:
            return '(%s %s)' % (subject, self.cue[0])
        elif len(self.operands) == 1:
            return '(%s %s %r)' % (subject, self.cue[0], self.operands[0])
        else:
            pairs = zip(self.cue, self.operands)
            return '(%s%s)' % (subject,
                               ''.join(' %s %r' % pair for pair in pairs))

def evrands_k(subject, (self, env), k):
    return evrands(self.operands, env, (call_k, (subject, self), k))

def call_k(arguments, (subject, self), k):
    return call(subject, self.cue, arguments, k)

def evrands(operands, env, k):
    if not operands:
        return k, ()
    else:
        return operands[0].eval(env, (evrands_more_k, (operands[1:], env), k))

def evrands_more_k(val, (operands, env), k):
    return evrands(operands, env, (evrands_cons_k, val, k))

def evrands_cons_k(vals, val, k):
    return k, (val,)+vals
