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
    def pp(self, out):
        out.pr(repr(self))

class Fetch(namedtuple('_Fetch', 'name')):
    vtable = expr_vtable
    def defs(self):
        return ()
    def eval(self, env, k):
        return k, env.get(self.name)
    def __repr__(self):
        return str(self.name)
    def pp(self, out):
        out.pr(repr(self))

class Then(namedtuple('_Then', 'expr1 expr2')):
    vtable = expr_vtable
    def defs(self):
        return combine(self.expr1.defs(), self.expr2.defs())
    def eval(self, env, k):
        return self.expr1.eval(env, (then_k, (self, env), k))
    def __repr__(self):
        return '%r; %r' % (self.expr1, self.expr2)
    def pp(self, out):
        self.expr1.pp(out)
        out.newline()
        self.expr2.pp(out)

def combine(defs1, defs2):
    if set(defs1) & set(defs2):
        raise Exception("Duplicate definitions")
    return defs1 + defs2

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
    def pp(self, out):
        out.pr('{')
        out.indent(4)
        out.newline()
        self.expr.pp(out)
        out.indent(-4)
        out.newline()
        out.pr('}')

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
        fmt = '%s %r' if isinstance(self.expr, Actor) else '%s ::= %r'
        return fmt % (self.var, self.expr)
    def pp(self, out):
        out.pr(self.var)
        out.pr(' ' if isinstance(self.expr, Actor) else ' ::= ')
        self.expr.pp(out)

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
        return ':: {%s}' % '; '.join(sorted(map(repr, self.value_vtable.values())))
    def pp(self, out):
        out.pr(':: {')
        out.indent(4)
        for method in sorted(self.value_vtable.values(),
                             key=lambda method: method.header()):
            out.newline()
            method.pp(out)
        out.indent(-4)
        out.newline()
        out.pr('}')

class Method(namedtuple('_Method', 'cue params expr')):
    def __call__(self, receiver, arguments, k):
        return self.expr.eval(extend(receiver.env, self.params, arguments), k)
    def __repr__(self):
        return '%s: %r' % (self.header(), self.expr)
    def header(self):
        if not self.params:
            assert len(self.cue) == 1
            return self.cue[0]
        else:
            return ' '.join(map(' '.join, zip(self.cue, self.params)))
    def pp(self, out):
        out.pr(self.header())
        out.pr(': ')
        self.expr.pp(out)

class Thing(object):
    def __init__(self, env, vtable):
        self.env = env
        self.vtable = vtable
    def __repr__(self):
        return '<%r %r>' % (self.env, self.vtable)

class Call(namedtuple('_Call', 'subject cue operands')):
    vtable = expr_vtable
    def defs(self):
        return reduce(combine, (expr.defs() for expr in (self.subject,) + self.operands))
    def eval(self, env, k):
        return self.subject.eval(env, (evrands_k, (self, env), k))
    def __repr__(self):
        if not self.operands:
            assert len(self.cue) == 1
            return '(%r %s)' % (self.subject, self.cue[0])
        else:
            pairs = zip(self.cue, self.operands)
            return '(%r%s)' % (self.subject,
                               ''.join(' %s %r' % pair for pair in pairs))
    def pp(self, out):
        out.pr('(')
        self.subject.pp(out)
        if not self.operands:
            out.pr(' ' + self.cue[0])
        else:
            for k, operand in zip(self.cue, self.operands):
                out.pr(' ' + k + ' ')
                operand.pp(out)
        out.pr(')')

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
